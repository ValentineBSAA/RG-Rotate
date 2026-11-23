"""User-facing transfer text. Previews are never confused with verified copies."""
from __future__ import annotations


def preview_explanation(plan, pretty_bytes) -> tuple[str, str, str]:
    """Return (preview summary, call-to-action, activity status)."""
    lines = [f"Files on virtual card: {plan.files:,} ({pretty_bytes(plan.bytes_total)})",
             f"New data required: {pretty_bytes(plan.bytes_new)}",
             f"Destination free: {pretty_bytes(plan.current_target_free)}"]
    if plan.conflicts:
        lines.append('Needs attention: ' + ' • '.join(plan.conflicts[:5]))
        return ('\n'.join(lines), 'Resolve conflicts before copying', 'Preview found conflicts; nothing copied.')
    if not plan.files:
        lines.append('No staged files yet. Import a game or prepare Android APKs first.')
        return ('\n'.join(lines), 'Add Files Before Copying', 'Preview complete: virtual card is empty.')
    matches = getattr(plan, 'existing_files', 0)
    if matches:
        lines.append(f"Already present by name and size: {matches:,} file(s) ({pretty_bytes(plan.bytes_already_present)})")
    if plan.files and matches == plan.files and plan.bytes_new == 0:
        lines.append('IMPORTANT: This preview did NOT hash-verify the existing files.')
        lines.append('Next: verify all existing files using SHA-256; no re-copying if identical.')
        action = f'✓  Verify {plan.files:,} existing file(s) (SHA-256)'
        status = f'Preview ready: 0 B to copy; {plan.files:,} existing file(s) still need verification.'
    elif plan.bytes_new == 0:
        lines.append('No new bytes expected. Existing files still require SHA-256 verification.')
        action = '✓  Verify existing files (SHA-256)'
        status = 'Preview ready: no new bytes expected; hash verification still pending.'
    else:
        lines.append('Next: copy new files, then SHA-256 verify every resulting file.')
        action = '⇄  Copy and Verify Files'
        status = f'Preview ready: {pretty_bytes(plan.bytes_new)} to copy. Nothing transferred yet.'
    lines.append('Practice folder: no actual microSD involved.' if plan.is_simulation else
                 'Real microSD: 8 GiB free-space reserve is enforced during copying.')
    return ('\n'.join(lines), action, status)


def copy_explanation(result: dict, is_simulation: bool) -> tuple[str, str, str, bool]:
    """Return (on-page summary, popup title, popup body, success)."""
    copied = int(result.get('copied', 0))
    skipped = int(result.get('skipped', 0))
    verified = int(result.get('verified', 0))
    files = int(result.get('files', 0))
    errors = list(result.get('errors', []))
    stopped = bool(result.get('cancelled'))
    success = not stopped and not errors and files > 0 and verified == files
    summary = (f'New files copied: {copied:,} • Existing identical files: {skipped:,} • '
               f'SHA-256 verified: {verified:,}/{files:,}')
    if stopped:
        summary += '\nCopy stopped. Any incomplete .retro-part files will be checked before resuming.'
    if errors:
        summary += '\nIssues: ' + ' • '.join(errors[:5])
    if success and copied == 0:
        heading = 'All existing files verified • Nothing needed copying'
    elif success:
        heading = 'Copy complete • Every file verified'
    else:
        heading = 'Copy needs attention'
    if success:
        closing = ('\n\nPractice copy complete. This is a normal Windows test folder, not a microSD card.'
                   if is_simulation else '\n\nReal microSD transfer complete. Eject the card through Windows before removing it.')
    else:
        closing = '\n\nCheck the listed issues before retrying. Existing files are not overwritten.'
    return summary, heading, heading + '\n\n' + summary + closing, success
