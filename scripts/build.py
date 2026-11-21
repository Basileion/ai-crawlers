import sys, json, re; sys.path.insert(0, '/workspace/basileion-sites')
from common import Site, e
C = '2026-11-20'
B = json.load(open('/workspace/ai-crawlers/data/bots.json'))
JS = open('/workspace/ai-crawlers/scripts/robots.js').read()
slug = lambda t: t.lower()
KIND = {'training': 'AI training', 'search': 'AI / web search', 'user-fetch': 'User-requested fetch', 'ads': 'Ads validation', 'other': 'Other', 'agent-builder': 'Agent builder', 'dataset': 'Open crawl dataset', 'link-preview': 'Link preview'}
OPS = sorted(set(b['op'] for b in B))
s = Site('ai-crawlers', 'AI Crawler <span>Rules</span>', 'AI Crawler Rules',
         [('Checker', '/#check'), ('Generator', '/#gen'), ('All bots', '/bots/'), ('Guide', '/guides/block-ai-training-keep-ai-search/'), ('Change log', '/changes/')],
         f'<b>AI Crawler Rules</b> checks robots.txt against {len(B)} AI and search crawler tokens, using each operator\'s own documentation (checked {C}). Runs in your browser; nothing is uploaded. robots.txt is a request, not access control; some user-initiated fetchers say they may not follow it.', acc='#6b2f8a', acc2='#f1e9f6')
data = json.dumps([{k: b.get(k) for k in ('token', 'op', 'kind', 'robots', 'fallback', 'also')} for b in B])
app = f"""<script>{JS}
const BOTS={data};const KIND={json.dumps(KIND)};
function run(){{const t=document.getElementById('rt').value,p=document.getElementById('pth').value||'/';
document.getElementById('res').innerHTML='<table><thead><tr><th>Bot</th><th style="text-align:left">Operator</th><th style="text-align:left">Purpose</th><th style="text-align:left">Result for '+p.replace(/</g,'&lt;')+'</th><th style="text-align:left">Matched group / rule</th><th style="text-align:left">Follows robots.txt?</th></tr></thead><tbody>'+BOTS.map(b=>{{const r=evaluate(t,b,p);return '<tr><td><a href="{s.BASE}/bots/'+b.token.toLowerCase()+'/">'+b.token+'</a></td><td style="text-align:left">'+b.op+'</td><td style="text-align:left">'+KIND[b.kind]+'</td><td style="text-align:left" class="'+(r.ok?'ok':'no')+'">'+(r.ok?'Allowed':'Blocked')+'</td><td style="text-align:left">'+r.via+(r.rule?' · '+r.rule:'')+'</td><td style="text-align:left">'+b.robots+'</td></tr>'}}).join('')+'</tbody></table>'}}
document.getElementById('rt').addEventListener('input',run);document.getElementById('pth').addEventListener('input',run);run();
function gen(){{const lines=[];for(const b of BOTS){{const v=document.querySelector('input[name="g_'+b.token+'"]:checked');if(v&&v.value==='block')lines.push('User-agent: '+b.token+'\\nDisallow: /\\n')}}document.getElementById('gout').textContent=(lines.join('\\n')||'# No AI bots blocked\\n')+'\\nUser-agent: *\\nAllow: /\\n'}}
function preset(k){{for(const b of BOTS){{const block=k==='all'?['training','search','user-fetch','dataset','agent-builder','other','ads'].includes(b.kind)&&b.token!=='Googlebot'&&b.token!=='Applebot':k==='train'?(b.kind==='training'||b.kind==='dataset'):false;document.querySelector('input[name="g_'+b.token+'"][value="'+(block?'block':'allow')+'"]').checked=true}}gen()}}
document.getElementById('genf').addEventListener('change',gen);preset('train');
</script>"""
sample = "User-agent: *\nDisallow: /admin/\n\nUser-agent: GPTBot\nUser-agent: ClaudeBot\nUser-agent: Google-Extended\nDisallow: /\n"
rows = ''.join(f'<tr><td style="text-align:left"><a href="/bots/{slug(b["token"])}/">{e(b["token"])}</a></td><td style="text-align:left">{e(b["op"])}</td><td style="text-align:left">{e(KIND[b["kind"]])}</td><td><label style="flex-direction:row;display:inline-flex;gap:4px;margin:0"><input type="radio" style="min-width:0" name="g_{e(b["token"])}" value="allow">allow</label> <label style="flex-direction:row;display:inline-flex;gap:4px;margin:0"><input type="radio" style="min-width:0" name="g_{e(b["token"])}" value="block">block</label></td></tr>' for b in B)
ntrain = sum(1 for b in B if b['kind'] == 'training'); nuser = [b for b in B if b['kind'] == 'user-fetch']
body = f"""<p class="eb" style="margin-top:34px">AI crawlers · operator docs checked {C}</p><h1>Which AI bots does your robots.txt let in?</h1>
<p class="lede">Paste your robots.txt and see, bot by bot, whether {len(B)} AI and search crawlers from {len(OPS)} operators are allowed or blocked, which group they match, and whether the operator says the bot follows robots.txt at all.</p>
<div class="grid"><div class="card"><div class="mut">Tokens tracked</div><div class="big">{len(B)}</div><div>{', '.join(OPS)}</div></div>
<div class="card"><div class="mut">Training-only control tokens</div><div class="big">{ntrain}</div><div>Blocking them leaves search crawlers untouched</div></div>
<div class="card warn"><div class="mut">User-requested fetchers that may skip robots.txt</div><div class="big">{sum(1 for b in nuser if b['robots']!='yes')} of {len(nuser)}</div><div>Per their operators' docs. <a href="/guides/block-ai-training-keep-ai-search/">Guide</a></div></div></div>
<h2 id="check">Checker</h2><label style="display:flex">robots.txt<textarea id="rt" rows="10">{e(sample)}</textarea></label><p><label>Path to test<input id="pth" value="/"></label></p><div id="res" class="tw"></div>
<p class="note">Matching follows RFC 9309: a bot uses the group naming its token (case-insensitive), else the * group; the longest matching rule wins and Allow wins a tie; * and $ wildcards supported. Applebot falls back to Googlebot rules when not named (Apple docs). Google-CloudVertexBot also matches Googlebot (Google docs).</p>
<h2 id="gen">Generator</h2><p><button class="btn" onclick="preset('train')">Block AI training, keep AI search</button> <button class="btn" onclick="preset('all')" style="background:var(--mut)">Block all AI bots</button> <button class="btn" onclick="preset('none')" style="background:var(--mut)">Allow all</button></p>
<form id="genf" onsubmit="return false"><div class="tw"><table><thead><tr><th style="text-align:left">Bot</th><th style="text-align:left">Operator</th><th style="text-align:left">Purpose</th><th>Rule</th></tr></thead><tbody>{rows}</tbody></table></div></form>
<h3>Your robots.txt groups</h3><pre id="gout"></pre><p class="note">"Block all AI bots" keeps Googlebot and Applebot (they power regular search) and uses Google-Extended and Applebot-Extended to opt out of AI training instead.</p>{app}"""
s.page('/', 'AI Crawler robots.txt Checker & Generator: GPTBot, ClaudeBot, PerplexityBot, Google-Extended | AI Crawler Rules',
       f'Check which of {len(B)} AI crawlers your robots.txt allows or blocks, and generate rules that block AI training but keep AI search. Sourced from OpenAI, Anthropic, Google, Apple, Perplexity, Meta and Common Crawl docs.', body,
       schema={'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'AI Crawler Rules', 'applicationCategory': 'DeveloperApplication', 'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': 0, 'priceCurrency': 'USD'}, 'url': s.SITE + '/'})
lis = ''
for b in B:
    same = [o for o in B if o['op'] == b['op'] and o['token'] != b['token']]
    body = f"""<p class="eb" style="margin-top:34px"><a href="/bots/">All bots</a> · {e(b['op'])} · checked {C}</p><h1>{e(b['token'])}: what it is and how to block it</h1>
<div class="card"><p><b>Operator:</b> {e(b['op'])} · <b>Purpose:</b> {e(KIND[b['kind']])} · <b>Follows robots.txt:</b> {e(b['robots'])}</p><p>{e(b['what'])}</p><p class="note">Source: <a href="{b['src']}" rel="nofollow noopener">{e(b['src'])}</a></p></div>
<h2>Block {e(b['token'])}</h2><pre>User-agent: {e(b['token'])}\nDisallow: /</pre><h2>Allow {e(b['token'])}</h2><pre>User-agent: {e(b['token'])}\nAllow: /</pre>
{'<p>Note: Apple says that if robots.txt does not mention Applebot but mentions Googlebot, Applebot follows the Googlebot rules.</p>' if b.get('fallback') else ''}
<p><a class="btn" href="/#check">Check your robots.txt</a></p><h2>Other {e(b['op'])} tokens</h2><ul>{''.join(f'<li><a href="/bots/{slug(o["token"])}/">{e(o["token"])}</a> ({e(KIND[o["kind"]])})</li>' for o in same) or '<li>None tracked</li>'}</ul>"""
    s.page(f'/bots/{slug(b["token"])}/', f'{b["token"]} ({b["op"]}): What It Does and How to Block It in robots.txt | AI Crawler Rules',
           f'{b["token"]} is {b["op"]}\'s {KIND[b["kind"]].lower()} bot. What it does, whether it follows robots.txt, and the exact rule to block or allow it. Source: {b["op"]} docs.', body)
    lis += f'<tr><td style="text-align:left"><a href="/bots/{slug(b["token"])}/">{e(b["token"])}</a></td><td style="text-align:left">{e(b["op"])}</td><td style="text-align:left">{e(KIND[b["kind"]])}</td><td style="text-align:left">{e(b["robots"])}</td></tr>'
s.page('/bots/', f'All {len(B)} AI Crawler User Agents (Nov 2026) | AI Crawler Rules', f'List of {len(B)} AI and search crawler robots.txt tokens with operator, purpose and robots.txt behavior.',
       f'<h1>All tracked AI crawler tokens</h1><div class="tw"><table><thead><tr><th style="text-align:left">Token</th><th style="text-align:left">Operator</th><th style="text-align:left">Purpose</th><th style="text-align:left">Follows robots.txt</th></tr></thead><tbody>{lis}</tbody></table></div>')
for op in OPS:
    bs = [b for b in B if b['op'] == op]
    s.page(f'/operators/{slug(op).replace(" ", "-")}/', f'{op} Crawlers and robots.txt Tokens | AI Crawler Rules', f'Every {op} crawler token tracked, what each does, and how to block training while keeping search.',
           f'<h1>{e(op)} crawlers</h1><ul>' + ''.join(f'<li><a href="/bots/{slug(b["token"])}/">{e(b["token"])}</a>: {e(b["what"])}</li>' for b in bs) + f'</ul><p class="note">Source: <a href="{bs[0]["src"]}" rel="nofollow noopener">{e(bs[0]["src"])}</a>, checked {C}.</p>')
train = [b for b in B if b['kind'] in ('training',)]
guide = f"""<p class="eb" style="margin-top:34px">Guide · checked {C}</p><h1>Block AI training, keep AI search: the robots.txt rules</h1>
<p class="lede">Several operators split training from search into separate tokens. Blocking only the training tokens keeps a site eligible for AI search answers, per each operator's documentation.</p>
<h2>Training-side tokens</h2><ul>{''.join(f'<li><a href="/bots/{slug(b["token"])}/">{e(b["token"])}</a> ({e(b["op"])}): {e(b["what"])}</li>' for b in train)}</ul>
<h2>Search-side tokens to leave allowed</h2><ul>{''.join(f'<li><a href="/bots/{slug(b["token"])}/">{e(b["token"])}</a> ({e(b["op"])})</li>' for b in B if b['kind']=='search')}</ul>
<h2>The rules</h2><pre>{''.join(f"User-agent: {b['token']}\n" for b in train)}Disallow: /</pre>
<h2>Caveats from the operators</h2><ul><li>OpenAI: ChatGPT-User fetches are user-initiated and "robots.txt rules may not apply".</li><li>Perplexity: Perplexity-User "generally ignores robots.txt rules".</li><li>Meta: meta-externalfetcher "may bypass robots.txt"; facebookexternalhit may bypass it for security checks.</li><li>Apple: Applebot-crawled data may be used to help train Apple models; Applebot-Extended is the opt-out token.</li><li>Google: Google-Extended does not affect Google Search inclusion or ranking.</li><li>Common Crawl's CCBot builds an open dataset available to anyone; blocking it is listed above as a dataset crawler, not a training token.</li></ul>
<p><a class="btn" href="/#gen">Generate your file</a></p>"""
s.page('/guides/block-ai-training-keep-ai-search/', 'How to Block AI Training but Keep AI Search Traffic (robots.txt, Nov 2026) | AI Crawler Rules',
       'The robots.txt tokens that opt out of AI training at OpenAI, Anthropic, Google, Apple and Meta while staying visible in ChatGPT, Claude, Perplexity and Meta AI search.', guide)
s.page('/about/', 'Methodology | AI Crawler Rules', 'How AI Crawler Rules sources bot data and evaluates robots.txt.', f"""<h1>Methodology</h1><ul>
<li>Every bot row comes from the operator's own crawler documentation, linked on its page, checked {C}. Third-party bot lists are not used.</li>
<li>The checker implements RFC 9309 matching in your browser. Nothing you paste leaves the page.</li>
<li>Operator-documented exceptions are applied: Applebot falls back to Googlebot rules; Google-CloudVertexBot also matches Googlebot.</li>
<li>"Follows robots.txt" quotes each operator's own statement. robots.txt is a request; it is not access control.</li></ul>""")
s.changes([{'date': C, 'title': f'Baseline: {len(B)} tokens from {len(OPS)} operators', 'text': 'First published snapshot of operator crawler documentation.'}], C)
s.finish(C, f'# AI Crawler Rules\n> robots.txt checker and generator for {len(B)} AI and search crawler tokens, sourced from operator docs ({C}).\n\n- Checker: {s.SITE}/\n- Guide: {s.SITE}/guides/block-ai-training-keep-ai-search/\n' + ''.join(f'- {b["token"]} ({b["op"]}): {s.SITE}/bots/{slug(b["token"])}/ source {b["src"]}\n' for b in B))
