// RFC 9309 robots.txt evaluation (groups, longest-match, allow wins ties, * and $ wildcards)
function parse(txt){const groups=[];let cur=null,lastUA=false;
 for(let raw of txt.split(/\r?\n/)){const line=raw.replace(/#.*/,'').trim();if(!line)continue;const m=line.match(/^([A-Za-z-]+)\s*:\s*(.*)$/);if(!m)continue;const k=m[1].toLowerCase(),v=m[2].trim();
  if(k==='user-agent'){if(!cur||!lastUA){cur={uas:[],rules:[]};groups.push(cur)}cur.uas.push(v.toLowerCase());lastUA=true}
  else if(k==='allow'||k==='disallow'){if(cur)cur.rules.push({allow:k==='allow',path:v});lastUA=false}
  else lastUA=false}
 return groups}
function groupFor(groups,token){const t=token.toLowerCase();let rules=[],hit=false;
 for(const g of groups)if(g.uas.includes(t)){hit=true;rules=rules.concat(g.rules)}
 return hit?rules:null}
function star(groups){let r=[],hit=false;for(const g of groups)if(g.uas.includes('*')){hit=true;r=r.concat(g.rules)}return hit?r:null}
function rx(p){let s='';for(const ch of p){if(ch==='*')s+='.*';else if(ch==='$')s+='$';else s+=ch.replace(/[.+?^{}()|[\]\\]/g,'\\$&')}return new RegExp('^'+s)}
function allowed(rules,path){let best=null;for(const r of rules){if(r.path===''){continue}if(rx(r.path).test(path)){const L=r.path.length;if(!best||L>best.L||(L===best.L&&r.allow&&!best.allow))best={L,allow:r.allow,rule:r}}}
 return best?{ok:best.allow,rule:(best.allow?'Allow: ':'Disallow: ')+best.rule.path}:{ok:true,rule:null}}
function evaluate(txt,bot,path){const g=parse(txt);let rules=groupFor(g,bot.token),via=bot.token;
 if(!rules&&bot.fallback){rules=groupFor(g,bot.fallback);if(rules)via=bot.fallback+' (fallback)'}
 if(!rules&&bot.also){for(const a of bot.also){rules=groupFor(g,a);if(rules){via=a;break}}}
 if(!rules){rules=star(g);via=rules?'*':'no matching group'}
 const r=rules?allowed(rules,path):{ok:true,rule:null};return{ok:r.ok,rule:r.rule,via}}
if(typeof module!=='undefined')module.exports={parse,evaluate};
