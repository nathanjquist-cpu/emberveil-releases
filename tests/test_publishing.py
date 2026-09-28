import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('publisher', Path(__file__).resolve().parents[1] / 'tools/publish.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PublishingRules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = {'Emberveil.exe': b'MZ tested executable', 'Emberveil.pck': b'GDPC tested game data'}
        self.request = {'version': '1.2.3', 'title': 'Emberveil test', 'release_notes': 'Reviewed test build.', 'zip': {'name': 'Emberveil-Windows-Prototype-1.2.3.zip'}, 'manifest': {'schema': 1, 'app': 'emberveil', 'platform': 'windows-x86_64', 'version': '1.2.3', 'save_version': 13, 'minimum_launcher': '1.0.0', 'files': {n: {'size': len(b), 'sha256': hashlib.sha256(b).hexdigest(), 'url': f'https://github.com/{p.REPO}/releases/download/v1.2.3/{n}'} for n, b in self.data.items()}}}
        self.archive = self.root / self.request['zip']['name']
        self.write_zip()

    def write_zip(self, extras=None):
        with zipfile.ZipFile(self.archive, 'w') as z:
            for name, b in self.data.items():
                z.writestr('Emberveil/' + name, b)
            z.writestr('Emberveil/CREDITS.md', 'Credits')
            z.writestr('Emberveil/licenses/License.txt', 'License')
            for name, b in (extras or {}).items():
                z.writestr(name, b)
        self.request['zip'].update(size=self.archive.stat().st_size, sha256=p.sha(self.archive))

    def test_good_package_preserves_exact_runtime_bytes(self):
        paths = p.prepare_assets(self.request, self.archive, self.root / 'output')
        self.assertEqual(len(paths), 5)
        for name, b in self.data.items():
            self.assertEqual((self.root / 'output' / name).read_bytes(), b)
        self.assertEqual(json.loads((self.root / 'output/release.json').read_text()), self.request['manifest'])

    def test_tampered_download_rejected(self):
        with self.archive.open('ab') as f:
            f.write(b'changed')
        with self.assertRaisesRegex(ValueError, 'approved build'):
            p.prepare_assets(self.request, self.archive, self.root / 'output')

    def test_wrong_inner_game_hash_rejected(self):
        self.request['manifest']['files']['Emberveil.exe']['sha256'] = 'a' * 64
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            p.prepare_assets(self.request, self.archive, self.root / 'output')

    def test_private_source_and_path_traversal_rejected(self):
        for name in ('Emberveil/scripts/player.gd', '../outside', 'Emberveil/../outside', 'Emberveil/secret.env', 'Emberveil/extra.exe', 'Emberveil\\escape'):
            with self.subTest(name=name):
                self.write_zip({name: b'not publishable'})
                with self.assertRaises(ValueError):
                    p.prepare_assets(self.request, self.archive, self.root / 'output')

    def test_manifest_cannot_redirect_launcher_elsewhere(self):
        self.request['manifest']['files']['Emberveil.exe']['url'] = 'https://example.com/anything.exe'
        with self.assertRaisesRegex(ValueError, 'launcher URL'):
            p.validate_request(self.request)

    def test_invalid_versions_rejected(self):
        for version in ('../1.2.3', '1.2.3;echo bad', 'v1.2.3', '1.2', '', None):
            with self.subTest(version=version), self.assertRaises(ValueError):
                p.version_tuple(version)

    def test_downgrade_or_same_version_never_becomes_latest(self):
        for version in ('0.9.0', '1.2.3'):
            with self.assertRaisesRegex(ValueError, 'older version'):
                p.require_newer(version, 'v1.2.3')
        p.require_newer('1.10.0', 'v1.2.3')

    def test_credits_are_deterministic_and_complete(self):
        p.prepare_assets(self.request, self.archive, self.root / 'a')
        p.prepare_assets(self.request, self.archive, self.root / 'b')
        name = 'Emberveil-Credits-and-Licenses-1.2.3.zip'
        self.assertEqual(p.sha(self.root / 'a' / name), p.sha(self.root / 'b' / name))
        with zipfile.ZipFile(self.root / 'a' / name) as z:
            self.assertEqual(set(z.namelist()), {'Emberveil/CREDITS.md', 'Emberveil/licenses/License.txt'})

    def test_server_digest_failure_rejected(self):
        paths = p.prepare_assets(self.request, self.archive, self.root / 'output')
        release = {'assets': [{'name': x.name, 'state': 'uploaded', 'size': x.stat().st_size, 'digest': 'sha256:' + p.sha(x)} for x in paths]}
        p.verify_remote_assets(release, paths)
        release['assets'][0]['digest'] = 'sha256:' + '0' * 64
        with self.assertRaisesRegex(ValueError, 'Remote asset'):
            p.verify_remote_assets(release, paths)

    def test_failed_upload_never_publishes_draft(self):
        (self.root / 'requests').mkdir()
        (self.root / 'requests/1.2.3.json').write_text(json.dumps(self.request))
        stage = {'tag_name': 'staging-v1.2.3', 'draft': False, 'prerelease': True, 'assets': [{'name': self.archive.name, 'state': 'uploaded', 'size': self.archive.stat().st_size, 'digest': 'sha256:' + p.sha(self.archive)}]}
        api_calls = []

        def fake_api(path, method='GET', payload=None):
            api_calls.append((path, method))
            if path == 'releases/tags/staging-v1.2.3':
                return stage
            if path == 'releases/latest':
                return {'tag_name': 'v1.2.2'}
            if method == 'POST':
                return {'id': 123, 'draft': True}
            raise AssertionError('Unexpected API mutation: ' + method)

        def fake_gh(*args):
            if args[:2] == ('release', 'download'):
                target = Path(args[args.index('--dir') + 1]) / self.archive.name
                target.write_bytes(self.archive.read_bytes())
                return ''
            if args[0] == 'api':
                return '[[]]'
            if args[:2] == ('release', 'upload'):
                raise RuntimeError('Simulated network failure during upload')
            raise AssertionError(args)

        with patch.object(p, 'ROOT', self.root), patch.object(p, 'api', fake_api), patch.object(p, 'gh', fake_gh):
            with self.assertRaisesRegex(RuntimeError, 'network failure'):
                p.publish('1.2.3', 'publish')
        self.assertIn(('releases', 'POST'), api_calls)
        self.assertFalse(any(method == 'PATCH' for _, method in api_calls))


if __name__ == '__main__':
    unittest.main()
