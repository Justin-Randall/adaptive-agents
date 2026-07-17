const C=document.getElementById('content'),S=document.getElementById('status');let currentPath=null;
function ready(fn){if(typeof marked!=='undefined'&&marked){fn()}else setTimeout(()=>ready(fn),50)}
function showStatus(msg,duration){S.textContent=msg;S.classList.remove('hidden');clearTimeout(S._timer);if(duration)S._timer=setTimeout(()=>S.classList.add('hidden'),duration)}
function escapeHtml(t){const e=document.createElement('div');e.textContent=t;return e.innerHTML}
function navigateTo(path,pushState){
 if(path===currentPath)return;currentPath=path;loadFile(path);
 if(pushState!==false){const url='/view?path='+encodeURIComponent(path);history.pushState({path},'',url)}
}
async function loadFile(path){
 try{const r=await fetch('/api/file?path='+encodeURIComponent(path));if(!r.ok)throw new Error('HTTP '+r.status);const t=await r.text(),h=marked.parse(t);C.innerHTML=h;showStatus('Loaded: '+path,2000);C.querySelectorAll('a[href]').forEach(anchorHandler)}
 catch(e){C.innerHTML='<p style="color:red">Error loading <code>'+escapeHtml(path)+'</code>: '+escapeHtml(e.message)+'</p>'}
}
function anchorHandler(a){const h=a.getAttribute('href');if(!h)return;if(h.startsWith('http://')||h.startsWith('https://')||h.startsWith('mailto:')||h.startsWith('#'))return;if(h.endsWith('.md')){a.addEventListener('click',e=>{e.preventDefault();navigateTo(resolvePath(currentPath||'',h))})}}
function resolvePath(base,target){if(target.startsWith('/'))return target.slice(1);const parts=base.split('/').slice(0,-1).concat(target.split('/')),result=[];for(const p of parts){if(p==='.'||p==='')continue;if(p==='..'){result.pop();continue}result.push(p)}return result.join('/')}
window.addEventListener('popstate',e=>{const p=new URLSearchParams(location.search).get('path')||(e.state&&e.state.path)||null;if(p)navigateTo(p,false);else navigateTo('.adaptive-agents/INDEX.md',false)})
function connectSSE(){const s=new EventSource('/events');s.addEventListener('file_changed',e=>{const d=JSON.parse(e.data);if(d.path===currentPath)loadFile(currentPath)});s.onerror=()=>showStatus('SSE reconnecting...',3000)}
ready(()=>{marked.use({breaks:true,gfm:true});connectSSE();const ip=new URLSearchParams(location.search).get('path');if(ip)navigateTo(ip,false);else navigateTo('.adaptive-agents/INDEX.md',false)})

