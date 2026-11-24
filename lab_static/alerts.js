"use strict";
/* UPAR KI BANNER KHABAR: result aane ke baad kaun se current pattern NAYE active hue (/api/alerts). Naya aaye to dikhta hai; x se hat jata hai (is phone me). */
(function(){
const KEY="alert_seen";
function seen(){try{return localStorage.getItem(KEY)||""}catch(e){return ""}}
function mark(id){try{localStorage.setItem(KEY,id)}catch(e){}}
function bar(){let b=document.getElementById("alert-bar");if(!b){b=document.createElement("div");b.id="alert-bar";const h=document.querySelector("header");(h&&h.parentNode)?h.after(b):document.body.prepend(b)}return b}
function nums(it){const n=(it.numbers||[]).map(x=>String(x).padStart(2,"0")).join("/");return n?`${it.name||""} (${(it.games||[]).join("+")} ${n})`:(it.name||"")}
function draw(j){
 const b=bar(),al=(j.items||[])[0],p=j.partial;
 const parts=[];
 if(al&&al.id!==seen()){
  const t=String(al.time||"").replace("T"," ").slice(11,16);
  parts.push(el("div",{class:"al-card"},
   el("div",{class:"al-top"},el("b",{},"Nayi khabar"),el("span",{class:"mut small"}," "+t),el("button",{type:"button",class:"al-x","aria-label":"Band karo",on:{click:()=>{mark(al.id);draw(j)}}},"×")),
   el("div",{class:"small"},al.label||""),
   el("ul",{class:"small al-ul"},(al.groups||[]).map(g=>el("li",{},el("b",{},`${g.naam} ${g.count}`),g.items&&g.items.length?": "+g.items.map(nums).join(", "):" (sab Active tab me)"))),
   el("button",{type:"button",class:"b sm",on:{click:()=>{mark(al.id);draw(j);go("active")}}},"Active tab kholo")));
 }
 if(p&&p.results&&Object.keys(p.results).length)parts.push(el("div",{class:"al-part small"},"Aaj aa chuke: ",Object.entries(p.results).map(([g,n])=>`${g} ${String(n).padStart(2,"0")}`).join(" · "),el("span",{class:"mut"}," (DS agli subah; line tab poori)")));
 b.replaceChildren(...parts);b.style.display=parts.length?"block":"none"}
async function tick(){try{const r=await fetch("/api/alerts");if(r.ok)draw(await r.json())}catch(e){}}
window.addEventListener("load",()=>{tick();setInterval(tick,60000)});
document.addEventListener("visibilitychange",()=>{if(!document.hidden)tick()});
})();
