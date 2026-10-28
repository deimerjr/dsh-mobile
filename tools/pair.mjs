#!/usr/bin/env node
/**
 * Cross-platform pairing helper: starts the DSH web profile, waits for the
 * tokenized URL and prints a QR code for the DSH Mobile app.
 *
 * Usage: node tools/pair.mjs [--port 3080] [--host 127.0.0.1] [--public-url URL] [--trusted-host HOST]
 */
import { spawn } from 'node:child_process';
import qrcode from 'qrcode-terminal';

const argv = process.argv.slice(2);
const opts = { port: '3080', host: '', publicUrl: '', trustedHosts: [] };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--port') opts.port = argv[++i];
  else if (a === '--host') opts.host = argv[++i];
  else if (a === '--public-url') opts.publicUrl = argv[++i];
  else if (a === '--trusted-host') opts.trustedHosts.push(argv[++i]);
  else if (a === '--help' || a === '-h') { console.log('See the header of tools/pair.mjs'); process.exit(0); }
  else { console.error('Unknown option: ' + a); process.exit(1); }
}

const args = ['--yes', '@deepseek-ai/dsh', 'web', '--no-open', '--port', opts.port];
if (opts.host) args.push('--host', opts.host);
if (opts.publicUrl) args.push('--public-url', opts.publicUrl);
for (const h of opts.trustedHosts) args.push('--trusted-host', h);

console.log('Starting: npx ' + args.join(' '));
console.log('(the first run downloads DSH; it can take a while)');
console.log('');

const child = spawn('npx', args, { stdio: ['ignore', 'pipe', 'pipe'], shell: process.platform === 'win32' });
let buf = '';
let printed = false;

function printPair(url) {
  printed = true;
  console.log('');
  console.log('Pairing URL (contains a process token - do not share):');
  console.log('  ' + url);
  console.log('');
  qrcode.generate(url, { small: true });
  console.log('');
  console.log('In DSH Mobile: Olvidar (if paired) -> Scan QR, or paste the URL.');
  console.log('Press Ctrl+C to stop DSH.');
  console.log('');
}

child.stdout.on('data', (d) => {
  const s = d.toString();
  process.stdout.write(s);
  if (!printed) {
    buf += s;
    const m = buf.match(/dsh web: (https?:\/\/\S+)/);
    if (m) printPair(m[1]);
  }
});
child.stderr.on('data', (d) => process.stderr.write(d.toString()));
child.on('exit', (code) => process.exit(code === null ? 0 : code));

process.on('SIGINT', () => { child.kill('SIGINT'); });
process.on('SIGTERM', () => { child.kill('SIGTERM'); });
