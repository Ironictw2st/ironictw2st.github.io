/* tools/scripts/tool_release.js
 *
 * Renders the version chip and the download / link buttons for one tool from TOOLS_DATA
 * (total_war/data/tools.js, written by generate_data/fetch_tool_docs.py).
 *
 * TOOLS_DATA can be stale or absent - a release happens far more often than this site is
 * regenerated - so nothing here depends on it being present. The download button always
 * points at the repo's permanent /releases/latest URL, which is correct whatever the data
 * says; only the version text and file size come from TOOLS_DATA.
 */

function escapeHtml(str) {
    return String(str == null ? '' : str)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function formatSize(bytes) {
    if (!bytes) return '';
    const mb = bytes / (1024 * 1024);
    return mb >= 1 ? mb.toFixed(1) + ' MB' : Math.round(bytes / 1024) + ' KB';
}

function formatDate(iso) {
    if (!iso) return '';
    const d = new Date(iso + 'T00:00:00Z');
    if (isNaN(d)) return '';
    return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
}

/* Repo URLs are the one thing we must be able to render without TOOLS_DATA. */
const TOOL_FALLBACK = {
    mod_manager: { name: 'TK Mod Manager', repo: 'Ironictw2st/TKModManager' },
    script_extender: { name: 'TK Script Extender', repo: 'Ironictw2st/TK-ScriptExtender' }
};

function toolInfo(key) {
    const live = (typeof TOOLS_DATA !== 'undefined' && TOOLS_DATA) ? TOOLS_DATA[key] : null;
    const fb = TOOL_FALLBACK[key] || {};
    const repo = (live && live.repo) || fb.repo || '';
    return {
        name: (live && live.name) || fb.name || '',
        repo: repo,
        url: (live && live.url) || (repo ? 'https://github.com/' + repo : ''),
        latest_url: (live && live.latest_url) || (repo ? 'https://github.com/' + repo + '/releases/latest' : ''),
        version: (live && live.version) || '',
        published: (live && live.published) || '',
        prerelease: !!(live && live.prerelease),
        asset: (live && live.asset) || '',
        asset_size: (live && live.asset_size) || 0
    };
}

function chipHtml(info) {
    if (!info.version) {
        return '<span class="ver-chip unknown">Latest release on GitHub</span>';
    }
    const date = formatDate(info.published);
    return '<span class="ver-chip">' + escapeHtml(info.version)
        + (info.prerelease ? ' <span class="ver-date">pre-release</span>' : '')
        + (date ? ' <span class="ver-date">' + escapeHtml(date) + '</span>' : '')
        + '</span>';
}

/**
 * @param key      'mod_manager' | 'script_extender'
 * @param chipId   element id for the version chip (may be null)
 * @param actionId element id for the button row (may be null)
 * @param extra    [{label, href}] links rendered after the download button
 */
function renderRelease(key, chipId, actionId, extra) {
    const info = toolInfo(key);

    const chip = chipId && document.getElementById(chipId);
    if (chip) chip.innerHTML = chipHtml(info);

    const row = actionId && document.getElementById(actionId);
    if (!row) return;

    const size = formatSize(info.asset_size);
    const dl = info.asset
        ? 'Download ' + info.asset + (size ? ' (' + size + ')' : '')
        : 'Download latest';

    let html = '<a class="link-btn github" href="' + escapeHtml(info.latest_url)
        + '" target="_blank" rel="noopener">' + escapeHtml(dl) + '</a>';

    (extra || []).forEach(function (e) {
        html += '<a class="link-btn" href="' + escapeHtml(e.href) + '">' + escapeHtml(e.label) + '</a>';
    });

    html += '<a class="link-btn github" href="' + escapeHtml(info.url)
        + '" target="_blank" rel="noopener">Source</a>';

    row.innerHTML = html;
}
