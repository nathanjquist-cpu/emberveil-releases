"""Publish only an approved, byte-verified game ZIP. Never execute its contents."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tempfile
import zipfile

REPO = 'nathanjquist-cpu/emberveil-releases'
ROOT = Path(__file__).resolve().parents[1]
GAME_FILES = {'Emberveil.exe', 'Emberveil.pck'}
DOCS = {'README.md', 'CREDITS.md', 'VALIDATION.md', 'GRAPHICS-STUDY.md', 'ILLUSTRATED-STUDY.md'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def version_tuple(version):
    require(isinstance(version, str) and re.fullmatch(r'\d+\.\d+\.\d+', version), 'Invalid version')
    return tuple(map(int, version.split('.')))


def sha(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def gh(*args):
    result = subprocess.run(['gh', *args], check=True, text=True, capture_output=True, timeout=900)
    return result.stdout


def api(path, method='GET', payload=None):
    args = ['api', f'repos/{REPO}/{path}', '--method', method]
    if payload is None:
        return json.loads(gh(*args))
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as f:
        json.dump(payload, f)
        f.flush()
        return json.loads(gh(*args, '--input', f.name))


def validate_request(request):
    version = request['version']
    version_tuple(version)
    z = request['zip']
    require(z['name'] == f'Emberveil-Windows-Prototype-{version}.zip', 'Unexpected ZIP name')
    require(type(z['size']) is int and 0 < z['size'] < 1024**3, 'Invalid ZIP size')
    require(re.fullmatch('[0-9a-f]{64}', z['sha256']), 'Invalid ZIP hash')
    m = request['manifest']
    require(m['schema'] == 1 and m['app'] == 'emberveil' and m['platform'] == 'windows-x86_64', 'Wrong app or platform')
    require(m['version'] == version and type(m['save_version']) is int and m['save_version'] > 0, 'Wrong game/save version')
    version_tuple(m['minimum_launcher'])
    require(set(m['files']) == GAME_FILES, 'Manifest must contain exactly the game EXE and PCK')
    for name, data in m['files'].items():
        require(data['url'] == f'https://github.com/{REPO}/releases/download/v{version}/{name}', 'Wrong launcher URL')
        require(type(data['size']) is int and 0 < data['size'] < 2 * 1024**3, 'Invalid game file size')
        require(re.fullmatch('[0-9a-f]{64}', data['sha256']), 'Invalid game file hash')
    require(isinstance(request['title'], str) and 0 < len(request['title']) < 150, 'Invalid title')
    require(isinstance(request['release_notes'], str) and len(request['release_notes']) < 100000, 'Invalid notes')
    return request


def prepare_assets(request, archive_path, out):
    validate_request(request)
    expected = request['zip']
    require(archive_path.stat().st_size == expected['size'] and sha(archive_path) == expected['sha256'], 'ZIP does not match approved build')
    out.mkdir(parents=True, exist_ok=True)
    version = request['version']
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        require(len(names) == len(set(names)), 'Duplicate ZIP entries')
        require(sum(i.file_size for i in infos) < 3 * 1024**3, 'ZIP expands beyond allowed size')
        for info in infos:
            path = PurePosixPath(info.filename)
            require(not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename, 'Unsafe ZIP path')
            require(not stat.S_ISLNK(info.external_attr >> 16), 'ZIP contains a symbolic link')
            require(path.parts[0] == 'Emberveil', 'Unexpected package root')
            rel = '/'.join(path.parts[1:])
            if info.is_dir():
                require(rel in ('', 'licenses'), 'Unexpected package directory')
                continue
            allowed_doc = rel in DOCS or rel == f'CHANGES-{version}.md'
            allowed_license = len(path.parts) == 3 and path.parts[1] == 'licenses' and path.suffix.lower() in ('.txt', '.md')
            require(rel in GAME_FILES or allowed_doc or allowed_license, 'Unapproved ZIP member: ' + info.filename)
        for name, data in request['manifest']['files'].items():
            info = archive.getinfo('Emberveil/' + name)
            require(info.file_size == data['size'], 'Game file size mismatch: ' + name)
            with archive.open(info) as src, (out / name).open('wb') as dst:
                shutil.copyfileobj(src, dst)
            require(sha(out / name) == data['sha256'], 'Game file hash mismatch: ' + name)
        require('Emberveil/CREDITS.md' in names and any(n.startswith('Emberveil/licenses/') and not n.endswith('/') for n in names), 'Missing credits or licenses')
        credits = out / f'Emberveil-Credits-and-Licenses-{version}.zip'
        with zipfile.ZipFile(credits, 'w', zipfile.ZIP_DEFLATED) as target:
            for name in sorted(names):
                if name == 'Emberveil/CREDITS.md' or (name.startswith('Emberveil/licenses/') and not name.endswith('/')):
                    require(archive.getinfo(name).file_size < 10 * 1024**2, 'Oversized license')
                    info = zipfile.ZipInfo(name, (2020, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    target.writestr(info, archive.read(name))
    shutil.copyfile(archive_path, out / expected['name'])
    (out / 'release.json').write_text(json.dumps(request['manifest'], indent=2) + '\n', encoding='utf-8')
    return sorted(out.iterdir())


def verify_remote_assets(release, paths):
    assets = {a['name']: a for a in release['assets']}
    require(set(assets) == {p.name for p in paths}, 'Release asset list mismatch')
    for path in paths:
        a = assets[path.name]
        require(a['state'] == 'uploaded' and a['size'] == path.stat().st_size and a.get('digest') == 'sha256:' + sha(path), 'Remote asset verification failed: ' + path.name)


def require_newer(version, current):
    require(current.startswith('v') and version_tuple(version) > version_tuple(current[1:]), 'Refusing to replace latest with an equal or older version')


def inspect_live():
    release = api('releases/latest')
    require(not release['draft'] and not release['prerelease'], 'Latest release is not stable')
    with tempfile.TemporaryDirectory() as tmp:
        gh('release', 'download', release['tag_name'], '--repo', REPO, '--pattern', 'release.json', '--dir', tmp)
        m = json.loads((Path(tmp) / 'release.json').read_text())
        require(release['tag_name'] == 'v' + m['version'] and set(m['files']) == GAME_FILES, 'Live feed version or files mismatch')
        assets = {a['name']: a for a in release['assets']}
        for name, d in m['files'].items():
            require(d['url'] == f"https://github.com/{REPO}/releases/download/{release['tag_name']}/{name}", 'Live feed URL mismatch')
            require(assets[name]['size'] == d['size'] and assets[name].get('digest') == 'sha256:' + d['sha256'], 'Live feed disagrees with uploaded game')
    print('Live launcher feed and game asset digests agree:', release['tag_name'])


def publish(version, mode):
    version_tuple(version)
    require(mode in ('verify', 'publish'), 'Invalid mode')
    request = validate_request(json.loads((ROOT / 'requests' / f'{version}.json').read_text()))
    require(request['version'] == version, 'Request filename/version mismatch')
    stage = api(f'releases/tags/staging-v{version}')
    require(not stage['draft'] and stage['prerelease'], 'Staging release must be published as a prerelease')
    staged = [a for a in stage['assets'] if a['name'] == request['zip']['name']]
    require(len(staged) == 1 and staged[0]['state'] == 'uploaded' and staged[0]['size'] == request['zip']['size'], 'Staging ZIP missing or incomplete')
    require(staged[0].get('digest') == 'sha256:' + request['zip']['sha256'], 'Staged ZIP digest is not the approved build')
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        gh('release', 'download', stage['tag_name'], '--repo', REPO, '--pattern', request['zip']['name'], '--dir', tmp)
        paths = prepare_assets(request, root / request['zip']['name'], root / 'verified')
        print('Verified ZIP, game bytes, credits and launcher URLs for', version)
        if mode == 'verify':
            print('Verification only; no releases changed.')
            return
        tag = 'v' + version
        # Missing tag is distinguished from authorization, network and other API failures.
        releases = json.loads(gh('api', f'repos/{REPO}/releases', '--paginate', '--slurp'))
        existing = next((r for page in releases for r in page if r['tag_name'] == tag), None)
        if existing and not existing['draft']:
            verify_remote_assets(existing, paths)
            print('Already published with identical files; leaving latest selection unchanged.')
            return
        require_newer(version, api('releases/latest')['tag_name'])
        if existing:
            require(existing['name'] == request['title'], 'Existing draft was not created for this request')
            require({a['name'] for a in existing['assets']} <= {p.name for p in paths}, 'Existing draft has unexpected assets')
        else:
            existing = api('releases', 'POST', {'tag_name': tag, 'target_commitish': os.environ.get('GITHUB_SHA', 'main'), 'name': request['title'], 'body': request['release_notes'], 'draft': True, 'prerelease': False})
        gh('release', 'upload', tag, '--repo', REPO, '--clobber', *map(str, paths))
        release = api(f"releases/{existing['id']}")
        require(release['draft'], 'Release changed while uploading')
        verify_remote_assets(release, paths)
        require_newer(version, api('releases/latest')['tag_name'])
        api(f"releases/{existing['id']}", 'PATCH', {'draft': False, 'prerelease': False, 'make_latest': 'true', 'name': request['title'], 'body': request['release_notes']})
        inspect_live()
        require(api('releases/latest')['tag_name'] == tag, 'Published release is not latest')
        print('Published verified launcher update:', tag)
        if os.environ.get('GITHUB_STEP_SUMMARY'):
            with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
                f.write(f'## Emberveil {version} published\n\nAll five asset digests verified. Launcher feed points to {tag}.\n')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--event', action='store_true')
    p.add_argument('--inspect-live', action='store_true')
    args = p.parse_args()
    if args.inspect_live:
        inspect_live()
    elif args.event:
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
        require(os.environ.get('GITHUB_REPOSITORY') == REPO, 'Wrong publishing repository')
        if os.environ.get('GITHUB_EVENT_NAME') == 'release':
            release = event['release']
            require(release['prerelease'] and release['tag_name'].startswith('staging-v'), 'Not a staging release')
            publish(release['tag_name'][len('staging-v'):], 'publish')
        else:
            require(os.environ.get('GITHUB_EVENT_NAME') == 'workflow_dispatch', 'Unsupported event')
            publish(event['inputs']['version'], event['inputs']['mode'])
    else:
        p.error('Choose --event or --inspect-live')


if __name__ == '__main__':
    main()
