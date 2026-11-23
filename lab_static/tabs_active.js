"use strict";
/* ACTIVE: auto-bane patterns me se jo abhi chal rahe hain / pichle 1-3 din me pass hue, ek jagah */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const dm=s=>{if(!s)return"";const [y,m,d]=String(s).slice(0,10).split("-").map(Number);return d?d+" "+MN[m-1]:s};
const tm=s=>String(s||"").replace("T"," ").slice(0,16);
const SRC={auto:"auto",manual:"manual"};
tabs.active=async function(root){
 let days=3,rep=null,busy=false;
 try{days=+localStorage.getItem("act_days")||3}catch(e){}
 const strip=el("div",{class:"card act-strip"}),body=el("div");
 const skel=()=>body.replaceChildren(el("div",{class:"act-skel"}),el("div",{class:"act-skel"}),el("div",{class:"act-skel"}));
 async function load(post){
  skel();busy=true;
  try{if(SX())await SX().load();rep=await api(post?"POST":"GET","/active"+(post?"/scan":"?days="+days),post?{days}:undefined);
   if(post)toast(rep.errors&&rep.errors.length?"Scan hua, par kuch galti aayi (neeche dekho)":"Scan ho gaya");
   draw()}
  catch(e){body.replaceChildren(el("div",{class:"warn"},e.message));drawStrip()}
  finally{busy=false;drawStrip()}}
 function drawStrip(){
  const s=rep&&rep.scans,last=s&&s.last;
  const btn=el("button",{class:"b big2",on:{click:()=>{if(!busy)load(true)}}},busy?[el("span",{class:"spin"}),"Scan chal raha hai..."]:"Abhi scan karo");
  if(busy)btn.disabled=true;
  const seg=el("div",{class:"act-seg"},[1,2,3].map(d=>el("button",{class:d===days?"on":"",on:{click:()=>{if(busy||d===days)return;days=d;try{localStorage.setItem("act_days",d)}catch(e){}load(false)}}},d+" din")));
  strip.replaceChildren(...[
   el("div",{class:"act-last"},el("b",{},"Aakhri scan: "),last?`${SRC[last.source]||last.source}, ${tm(last.time)}`:"abhi tak aaj koi scan nahi hua"),
   s?el("div",{class:"row"},el("span",{class:"pill "+(s.auto_today>=2?"g":"o")},`Aaj auto scan: ${s.auto_today} (do hone chahiye)`),el("span",{class:"pill m"},`Manual: ${s.manual_today}`)):null,
   el("div",{class:"row"},btn,seg)].filter(Boolean));}
 function nums(t){return t&&t.numbers&&t.numbers.length?el("div",{class:"act-nums"},t.numbers.map(n=>el("span",{class:"chip green"},p2(n)))):null}
 const SX=()=>window.SCANX;
 function links(it){const sx=SX();return el("div",{class:"row"},
  sx?sx.seenUI(it.id,()=>draw()):null,sx?sx.editUI(it.id):null,
  el("button",{class:"b g sm",on:{click:()=>go("scan")}},"Pura dekho"),
  el("a",{href:"/api/scanner/view?id="+encodeURIComponent(it.id),target:"_blank"},el("button",{class:"b g sm"},"Rang chart")),
  el("a",{href:"/api/scanner/xlsx?id="+encodeURIComponent(it.id)},el("button",{class:"b g sm"},"Excel")))}
 function card(it,pass){
  const t=it.target;
  return el("div",{class:"act-card "+(pass?"pass":"now")+(SX()&&SX().reviewed(it.id)?" seen":"")},
   el("div",{class:"act-top"},el("b",{},it.title||it.name),
    pass?el("span",{class:"act-tag ok"},"PASS "+dm(it.resolved_on)):it.ambiguous?el("span",{class:"act-tag"},"confusion"):el("span",{class:"pill "+(it.strength==="mazboot"?"g":"m")},it.strength||"")),
   t?el("p",{class:"mut small",style:"margin:6px 0 0"},`${dm(t.date)}: ${t.games||""} me`):null,nums(t),
   (it.lines||[]).map(l=>el("p",{class:"mut small",style:"margin:3px 0"},l)),
   el("p",{class:"mut small",style:"margin:3px 0"},`Pehli baar dikha: ${dm(it.first_seen)}`),links(it))}
 function grouped(items,pass){
  const g=new Map();for(const it of items){const k=(it.pattern&&it.pattern.naam)||it.name;(g.get(k)||g.set(k,[]).get(k)).push(it)}
  return [...g].map(([k,v])=>el("div",{},el("div",{class:"act-grp"},`${k} (${v.length})`),v.map(i=>card(i,pass))))}
 function board(){
  const rows=rep.board||[];
  return rows.length?rows.map(r=>{const has=r.rate!=null;
   return el("div",{class:"act-row"},
    el("div",{class:"act-top"},el("b",{},r.naam),el("span",{class:"mut small"},has?`PASS ${r.pass} | FAIL ${r.fail} | ${Math.round(r.rate*(r.rate<=1?100:1))}%`:"abhi record nahi")),
    has?el("div",{class:"row",style:"margin-top:6px"},el("div",{class:"act-bar"},el("i",{style:`width:${Math.min(100,r.rate<=1?r.rate*100:r.rate)}%`}))):null,
    r.summary?el("p",{class:"mut small",style:"margin:4px 0 0"},r.summary):null)}):[el("p",{class:"mut"},"Abhi koi pattern record me nahi.")]}
 function draw(){
  const now=rep.now||[],pass=rep.recent_pass||[],n=rep.days||days;
  const sx=SX(),all=[...now,...pass],nd=sx?new Set(all.filter(i=>sx.reviewed(i.id)).map(i=>i.id)).size:0;
  body.replaceChildren(...[
   sx?el("p",{class:"small",style:"margin:0 0 6px"},el("b",{},`Aaj ka batch: ${nd} dekhe`)," ",el("span",{class:"mut"},`(kul ${new Set(all.map(i=>i.id)).size}; kal ke dekhe hue ginti me nahi)`)):null,
   rep.errors&&rep.errors.length?el("div",{class:"warn",style:"margin-bottom:10px"},el("b",{},"Kuch galti aayi:"),rep.errors.map(e=>el("p",{class:"small",style:"margin:3px 0"},typeof e==="string"?e:JSON.stringify(e)))):null,
   el("h2",{class:"act-h"},"Abhi chal rahe (aaj khelne layak)"),
   now.length?grouped(now,false):el("p",{class:"mut"},"Abhi koi pattern chal nahi raha. Naya ban-ne par yahan apne aap aa jayega."),
   el("h2",{class:"act-h"},`Pichle ${n} din me PASS hue`),
   pass.length?grouped(pass,true):el("p",{class:"mut"},`Pichle ${n} din me koi pass nahi hua.`),
   rep.recent_fail?el("p",{class:"mut small"},`Pichle ${n} din me ${rep.recent_fail} FAIL bhi hue.`):null,
   el("h2",{class:"act-h"},"Scoreboard (pichle 30 din)"),el("div",{class:"card flat"},board())].flat().filter(Boolean))}
 root.append(el("button",{type:"button",class:"card rk-link",on:{click:()=>go("rank")}},"Aaj ke number ranking dekho"),el("div",{class:"card"},el("h2",{style:"margin:0 0 4px"},"Active ",el("span",{class:"sub"},"(jo pattern abhi chal rahe hain)")),
  el("p",{class:"mut small",style:"margin:0"},"Ek baar bana pattern kabhi gayab nahi hota. Scan din me do baar apne aap hota hai.")),strip,body);
 drawStrip();await load(false);
};
})();
