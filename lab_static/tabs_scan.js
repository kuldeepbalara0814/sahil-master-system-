"use strict";
/* PATTERN SCAN: sikhaye hue pattern roz apne aap chalte hain; aaj kya ban raha hai, saaf rang me, Excel download */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const dm=s=>{const [y,m,d]=s.split("-").map(Number);return d+" "+MN[m-1]};
const G=["FB","GB","GL","DS"];
const ST={aaj:["o","Aaj ban raha"],pass:["g","PASS"],fail:["r","FAIL"],dekho:["m","dekho"]};
const SR={mazboot:["g","mazboot"],theek:["y","theek"],kamzor:["m","kamzor (random jaisa)"],info:["m","jaankari"]};


/* ---- shared: aaj ke dekhe hue pattern + Edit karo (tabs_active.js bhi yahi use karta hai) ---- */
const SX=window.SCANX=(()=>{
 let ids=new Set(),date="";
 const set=r=>{ids=new Set((r&&r.ids)||[]);date=(r&&r.date)||date;return ids};
 const o={
  async load(){try{set(await api("GET","/review"))}catch(e){}return ids},
  reviewed:id=>ids.has(id),count:()=>ids.size,
  async mark(list,done){set(await api("POST","/review",{ids:list,done}));return ids},
  async toggle(id){return o.mark([id],!ids.has(id))},
  async edit(id){const r=await api("POST","/scanner/to_board",{id});return (r&&r.boards)||[]},
  handoff(b){try{localStorage.setItem("pedit",JSON.stringify({from:b.from,months:b.months,name:b.name,cells:b.cells}))}catch(e){toast("Pattern edit ke liye save nahi ho paya");return}go("pattern")},
  /* "Edit karo" button; 2 board ho to 2 chhote button */
  editUI(id){
   const box=el("span",{class:"edwrap"}),b=el("button",{class:"b sm edbtn"},"Edit karo");
   b.onclick=async()=>{b.disabled=true;
    try{const bs=await o.edit(id);
     if(!bs.length)toast("Is pattern ka board nahi bana");
     else if(bs.length===1)o.handoff(bs[0]);
     else box.replaceChildren(...bs.map((x,i)=>el("button",{class:"b sm edbtn",on:{click:()=>o.handoff(x)}},(x.label||(i?"Naya":"Purana"))+" mahina Edit")))}
    catch(e){toast(e.message)}finally{b.disabled=false}};
   box.append(b);return box},
  /* "Dekh liya" toggle button; onchange() har badlav par chalta hai */
  seenUI(id,onchange){
   const b=el("button",{class:"b g sm seenbtn"});
   const paint=()=>{const d=ids.has(id);b.textContent=d?"\u2713 Dekh liya":"Dekh liya";b.classList.toggle("on",d);b.closest&&b.closest(".scard,.act-card")&&b.closest(".scard,.act-card").classList.toggle("seen",d)};
   b.onclick=async()=>{b.disabled=true;try{await o.toggle(id);paint();onchange&&onchange()}catch(e){toast(e.message)}finally{b.disabled=false}};
   paint();setTimeout(paint,0);return b}
 };return o})();

/* Step-sheet: ek lambi sheet, mahine upar se niche (Step 1, 2, 3), har step ki boundary moti border me */
const MFULL=["JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE","JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER"];
function stackSheet(st){
 const t=el("table",{class:"st-t"}),tb=el("tbody");
 t.append(el("colgroup",{},el("col",{class:"st-cd"}),...G.map(()=>el("col",{}))));
 t.append(el("thead",{},el("tr",{},["Tarikh",...G].map((h,i)=>el("th",{class:i?"":"st-d"},h)))));
 let ym=null;
 for(const r of st.rows){
  const k=r.date.slice(0,7);
  if(k!==ym){ym=k;tb.append(el("tr",{class:"st-mon"},el("th",{colspan:5},MFULL[+k.slice(5)-1]+" "+k.slice(0,4))))}
  const cls="st-r"+(r.step?" st-in":"")+(r.edge==="start"||r.edge==="startend"?" st-top":"")+(r.edge==="end"||r.edge==="startend"?" st-bot":"");
  const first=r.edge==="start"||r.edge==="startend";
  const d=el("td",{class:"st-d"},String(+r.date.slice(8)).padStart(2,"0")+" "+MN[+r.date.slice(5,7)-1]);
  if(first&&r.step)d.prepend(el("span",{class:"st-tag"},"STEP "+r.step));
  tb.append(el("tr",{class:cls,"data-step":String(r.step||0)},d,...[0,1,2,3].map(g=>{
   const kd=r.kind&&r.kind[g],txt=(r.txt&&r.txt[g])||(r.v?p2(r.v[g]):"");
   const td=el("td",{class:"st-c"+(kd?" st-"+kd:"")+(r.ind&&r.ind[g]?" st-red":"")},txt);
   const col=r.c&&r.c[g];
   if(col){td.style.background="#"+String(col).replace("#","");td.style.color="#000"}
   if(r.ind&&r.ind[g]){if(col)td.classList.add("st-redo");else{td.style.background="#FF5252";td.style.color="#000"}}
   return td})))}
 t.append(tb);
 return el("div",{},el("div",{class:"st-wrap"},t),
  el("div",{class:"st-leg"},(st.legend||[]).map(l=>el("div",{class:"st-li"},el("span",{class:"st-sw",style:"background:#"+String(l.color).replace("#","")}),el("span",{},l.text)))),
  st.note?el("p",{class:"mut small st-note"},st.note):null)}

function chart(v){
 if(v.stack){
  let mode="one";const body=el("div"),seg=el("div",{class:"st-seg"});
  const draw=()=>{
   seg.replaceChildren(el("button",{class:mode==="one"?"on":"","data-m":"one",on:{click:()=>{mode="one";draw()}}},"Ek sheet (upar Step 1, beech Step 2, niche Step 3)"),
    el("button",{class:mode==="blk"?"on":"","data-m":"blk",on:{click:()=>{mode="blk";draw()}}},"Side-by-side (3 block)"));
   body.replaceChildren(mode==="one"?stackSheet(v.stack):chartBlocks(v))};
  draw();return el("div",{},seg,body)}
 return chartBlocks(v)}

function chartBlocks(v){
 const t=el("table",{class:"sheet scn"}),th=el("thead"),tb=el("tbody");
 th.append(el("tr",{},v.blocks.map(b=>el("th",{class:"ttl2",colspan:5},b.label))));
 th.append(el("tr",{},v.blocks.flatMap(()=>["Tarikh",...G].map((h,i)=>el("th",{class:i==0?"d":"sh"},h)))));
 const n=Math.max(...v.blocks.map(b=>b.rows.length));
 for(let i=0;i<n;i++){
  tb.append(el("tr",{},v.blocks.flatMap(b=>{const r=b.rows[i];if(!r)return Array(5).fill(el("td",{}));
   const d=el("td",{class:"d"},r.date&&r.date!=="aage"?dm(r.date):(r.date==="aage"?"aage":""));
   return [d,...[0,1,2,3].map(g=>{const txt=r.txt[g]||(r.v?p2(r.v[g]):"");const td=el("td",{class:"c"+(r.kind[g]?" "+r.kind[g]:"")},txt);
    if(r.c[g]){td.style.background="#"+r.c[g];td.style.color="#000"}if(r.kind[g]==="pass")td.style.outline="3px solid #000";if(r.kind[g]==="light")td.style.fontStyle="italic";return td})]})))}
 t.append(th,tb);return el("div",{},el("p",{class:"mut small"},v.note),el("div",{class:"sheetwrap fit",style:"max-height:none"},t));
}

/* family pattern: poora mahina, har rashi family alag rang; is pattern ke cell bold + moti border; neeche 'ye kaise bana' */
function famMonth(v){
 let mode="all",iso=null;const box=el("div"),tabs2=el("div",{class:"row"}),legend=el("div",{class:"row",style:"gap:6px"});
 const selk=new Map(v.sel.map(c=>[c.date+"|"+c.g,c]));
 const lighten=h=>{const n=parseInt(h,16),r=(n>>16)&255,g=(n>>8)&255,b=n&255,f=c=>Math.round(c+(255-c)*.6);return "#"+[f(r),f(g),f(b)].map(x=>x.toString(16).padStart(2,"0")).join("")};
 function table(ym){
  const mo=v.months[ym],t=el("table",{class:"sheet scn mc"}),th=el("thead"),tb=el("tbody");
  th.append(el("tr",{},el("th",{class:"ttl2",colspan:5},mo.label.toUpperCase())));
  th.append(el("tr",{},["Tarikh",...G].map((h,i)=>el("th",{class:i==0?"d":"sh"},h))));
  for(const [d,vals] of mo.days){const day=+d.slice(8);
   tb.append(el("tr",{},el("td",{class:"d"},day+" "+MN[+d.slice(5,7)-1]),...[0,1,2,3].map(g=>{
    const s=selk.get(d+"|"+g),fi=v.cellfam[d+"|"+g];
    const show=fi!==undefined&&(mode==="all"?(iso===null||fi===iso):fi===v.sel_family);
    const td=el("td",{class:"c"},s&&s.text?s.text:(vals?p2(vals[g]):""));
    if(show){td.style.background="#"+v.families[fi].color;td.style.color="#000"}
    if(s){td.style.fontWeight="900";td.style.outline="3px solid "+(s.kind==="pass"?"#000":"#fff");td.style.outlineOffset="-3px";
     if(s.kind==="target"){td.style.background="#ffd0e6";td.style.color="#000";td.style.fontStyle="italic"}if(!show&&s.kind!=="target"){td.style.background="#555"}}
    return td})))}
  t.append(th,tb);return el("div",{class:"sheetwrap",style:"max-height:70vh;margin-bottom:8px"},t)}
 function draw(){
  box.replaceChildren(...Object.keys(v.months).map(table));
  tabs2.replaceChildren(
   el("button",{class:"b sm"+(mode==="all"?"":" g"),on:{click:()=>{mode="all";iso=null;draw()}}},"Sab family alag rang"),
   el("button",{class:"b sm"+(mode==="one"?"":" g"),on:{click:()=>{mode="one";draw()}}},"Sirf is pattern ki family"));
  legend.replaceChildren(...v.families.map((f,i)=>el("button",{class:"b g sm",title:f.numbers.map(p2).join(" "),style:"background:#"+f.color+";color:#000;border:"+(i===v.sel_family?"3px solid #000":"1px solid #888"),
   on:{click:()=>{mode="all";iso=(iso===i?null:i);draw()}}},f.name)))}
 draw();
 return el("div",{},el("div",{class:"card flat",style:"margin:6px 0"},el("b",{},"Ye kaise bana"),...v.explain.map(l=>el("p",{class:"mut small",style:"margin:3px 0"},l)),
   el("pre",{class:"small remark",style:"max-height:none"},v.timeline.join("\n"))),
  el("p",{class:"mut small"},"Har rashi family ka apna rang (rang par kaala ank). Is pattern ke cell moti safed border me, 3rd step gulabi '?'. Kisi family ke rang par dabao to sirf wahi family dikhegi (dobara dabao to sab)."),
  tabs2,el("div",{class:"row",style:"gap:6px"},legend),box)}

window.SCANX.chart=chart;window.SCANX.famMonth=famMonth;           // Active tab me map kholne ke liye
tabs.scan=async function(m){
 const unseen={};
 let rep=null,filter="all",plays={},sel=null,idx=[],mscope="recent";
 const info=el("p",{class:"mut small"}),errBox=el("div"),list=el("div"),runBtn=el("button",{class:"b"},"Script abhi chalao (manual)");
 const fsel=el("select",{on:{change:()=>{filter=fsel.value;draw()}}},[["all","Sab dikhao"],["aaj","Sirf aaj ke andaze wale"],["strong","Sirf mazboot/theek"]].map(([v,t])=>el("option",{value:v},t)));
 async function run(){
  runBtn.disabled=true;runBtn.textContent="Chal rahi hai...";
  try{rep=await api("POST","/scanner/run",{});toast(rep.errors.length?"Script chali par galti aayi (neeche dekho)":"Script poori chali, sab theek");draw()}
  catch(e){errBox.replaceChildren(el("div",{class:"warn"},"Script chali hi nahi: "+e.message))}
  finally{runBtn.disabled=false;runBtn.textContent="Script abhi chalao (manual)"}}
 runBtn.onclick=run;
 function card(it,ix0){
  const num=ix0==null?null:"Pattern "+String(ix0+1).padStart(2,"0");
  const view=el("div"),st=ST[it.status]||ST.dekho,sr=SR[it.strength]||SR.info;
  const open=el("button",{class:"b g sm"},"Kholo (rang me dekho)");let on=false;
  open.onclick=async()=>{on=!on;if(!on){view.replaceChildren();open.textContent="Kholo (rang me dekho)";return}
   open.textContent="Band karo";view.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load..."));
   try{view.replaceChildren(it.kind==="family"?famMonth(await api("GET","/scanner/month_view?id="+encodeURIComponent(it.id))):chart(await api("GET","/scanner/view?id="+encodeURIComponent(it.id))))}catch(e){view.replaceChildren(el("div",{class:"warn"},e.message))}};
  const panel=el("div"),saved=el("div"),pb=el("button",{class:"b g sm"},"Maine kahan kya khela");
  const showSaved=()=>{const q=plays[it.id];saved.replaceChildren(...(q?[el("p",{class:"ok small"},"Aap ka note: "+Object.entries(q.plays).map(([g,v])=>`${g}: ${v.numbers.map(p2).join(" ")} (${v.stake} Rs)`).join(" | ")+(q.note?" - "+q.note:""))]:[]))};
  showSaved();
  pb.onclick=()=>{
   if(panel.childNodes.length){panel.replaceChildren();return}
   const cur=(plays[it.id]||{}).plays||{},ins={},sts={};
   const noteIn=el("input",{type:"text",maxlength:200,placeholder:"Note (zaroori nahi)",style:"width:100%"});noteIn.value=(plays[it.id]||{}).note||"";
   const rows=G.map(g=>{const ni=el("input",{type:"text",placeholder:"number: 02 07 20 ...",style:"width:100%"}),ss=el("select",{},[5,10,15,20,30,40,50,100].map(v=>el("option",{value:v,selected:v===((cur[g]||{}).stake||10)},v+" Rs")));
    ni.value=((cur[g]||{}).numbers||[]).map(p2).join(" ");ins[g]=ni;sts[g]=ss;return el("div",{class:"row",style:"flex-wrap:nowrap"},el("b",{style:"width:28px"},g),ni,ss)});
   const parse=v=>[...new Set((v.match(/\d+/g)||[]).map(Number).filter(n=>n>=0&&n<=99))];
   const prefill=()=>{const nums=(it.target&&it.target.numbers)||[];const locs=(it.loc&&it.loc.length?it.loc:(it.target&&it.target.games?it.target.games.split(/[ ,]+/).filter(x=>G.includes(x)):[]));
    G.forEach(g=>{ins[g].value=nums.map(p2).join(" ");sts[g].value=String(locs.includes(g)?20:10)})};
   const save=async(clear)=>{const body={};if(!clear)G.forEach(g=>{const n=parse(ins[g].value);if(n.length)body[g]={numbers:n,stake:+sts[g].value}});
    try{await api("POST","/scanner/play",{id:it.id,plays:body,note:noteIn.value});
     if(Object.keys(body).length)plays[it.id]={plays:body,note:noteIn.value};else delete plays[it.id];
     showSaved();toast(Object.keys(body).length?"Note save ho gaya":"Note hata diya");panel.replaceChildren()}catch(e){toast(e.message)}};
   panel.replaceChildren(el("div",{class:"card flat",style:"margin-top:8px"},el("p",{class:"mut small"},"Har game me jo number khele wo likho (khaali = nahi khela). Paper rule: har number 10 Rs, location par 20 Rs."),...rows,noteIn,
    el("div",{class:"row"},el("button",{class:"b g sm",on:{click:prefill}},"Paper rule se bharo"),el("button",{class:"b sm",on:{click:()=>save(false)}},"Save"),el("button",{class:"b g sm",on:{click:()=>save(true)}},"Note hatao"))))};
  const seen=SX.seenUI(it.id,()=>draw());
  return el("div",{class:"card flat scard"+(SX.reviewed(it.id)?" seen":"")},
   el("div",{class:"row",style:"justify-content:space-between"},el("h3",{style:"margin:0"},num?el("span",{class:"pill m",style:"margin-right:8px"},num):null,it.name,it.new?el("span",{class:"pill g",style:"margin-left:8px"},"NAYA"):null),el("span",{},el("span",{class:"pill "+st[0]},st[1])," ",el("span",{class:"pill "+sr[0]},sr[1]))),
   el("div",{class:"b"},it.title),it.lines.map(l=>el("p",{class:"mut small",style:"margin:3px 0"},l)),
   it.target?el("p",{class:"tgt"},`Aaj ${dm(it.target.date)}: ${it.target.games} me `,el("b",{},it.target.numbers.map(p2).join(" ")),it.kind==="copy"?" (set ka koi bhi)":" (andaza)"):null,
   el("div",{class:"row"},seen,SX.editUI(it.id),open,pb,el("a",{href:"/api/scanner/xlsx?id="+encodeURIComponent(it.id)},el("button",{class:"b g sm"},"Excel download"))),saved,panel,view)}
 const idxBox=el("div"),detail=el("div");
 const lighten=h=>{const n=parseInt(h,16),r=(n>>16)&255,g=(n>>8)&255,b=n&255,f=c=>Math.round(c+(255-c)*.6);return "#"+[f(r),f(g),f(b)].map(x=>x.toString(16).padStart(2,"0")).join("")};
 /* ---- ek mahine ki sheet ki kai copy: har copy me ek pattern, alag rang ---- */
 function sheetTable(c,months,ym){
  const mo=months[ym],cells=new Map();for(const x of c.cells)cells.set(x.date+"|"+x.g,x);
  const t=el("table",{class:"sheet scn mc"}),th=el("thead"),tb=el("tbody");
  th.append(el("tr",{},el("th",{class:"ttl2",colspan:5},mo.label.toUpperCase())));
  th.append(el("tr",{},["Tarikh",...G].map((h,i)=>el("th",{class:i==0?"d":"sh"},h))));
  for(const [iso,v] of mo.days){const d=+iso.slice(8);
   tb.append(el("tr",{},el("td",{class:"d"},d+" "+MN[+iso.slice(5,7)-1]),...[0,1,2,3].map(g=>{const x=cells.get(iso+"|"+g);
    const td=el("td",{class:"c"},x&&x.text?x.text:(v?p2(v[g]):""));
    if(x){td.style.background=x.kind==="light"?lighten(c.color):"#"+c.color;td.style.color="#000";td.style.fontWeight="800";if(x.kind==="pass")td.style.outline="3px solid #000";if(x.kind==="light")td.style.fontStyle="italic"}
    return td})))}
  t.append(th,tb);return t}
 function copiesView(data){
  const wrap=el("div",{class:"mcopies"});
  data.copies.forEach((c,n)=>{
   const st=ST[c.status]||ST.dekho;
   wrap.append(el("div",{class:"mcopy"},
    el("div",{class:"mh2",style:"background:#"+c.color},el("b",{},`Copy ${n+1}: ${c.name}`)," ",el("span",{class:"pill "+st[0]},st[1])),
    el("div",{class:"small",style:"margin:4px 0"},c.title.split(": ").slice(1).join(": ")),
    el("pre",{class:"small remark"},c.remark),
    ...c.ym.map(ym=>el("div",{class:"sheetwrap",style:"max-height:none;margin-bottom:6px"},sheetTable(c,data.months,ym)))))});
  return wrap}
 function drawPng(data,key){
  const cv=document.createElement("canvas"),ctx=cv.getContext&&cv.getContext("2d");if(!ctx){toast("Is browser me image nahi ban sakti");return}
  const W=232,H=22,pad=14,cols=Math.min(4,Math.max(1,data.copies.length)),lh=p=>56+p.ym.length*(26+22+31*H+10);
  const rowsH=[];for(let i=0;i<data.copies.length;i+=cols)rowsH.push(Math.max(...data.copies.slice(i,i+cols).map(lh)));
  cv.width=cols*(W+pad)+pad;cv.height=rowsH.reduce((a,b)=>a+b+pad,pad)+30;
  ctx.fillStyle="#111";ctx.fillRect(0,0,cv.width,cv.height);ctx.fillStyle="#fff";ctx.font="bold 16px sans-serif";ctx.fillText(`${key} pattern: ${data.copies.length} copy (alag rang)`,pad,22);
  let y0=30;
  data.copies.forEach((c,k)=>{const col=k%cols,row=Math.floor(k/cols);if(col===0&&row>0)y0+=rowsH[row-1]+pad;const x0=pad+col*(W+pad);let y=y0+pad/2;
   ctx.fillStyle="#"+c.color;ctx.fillRect(x0,y,W,22);ctx.fillStyle="#000";ctx.font="bold 13px sans-serif";ctx.fillText(`Copy ${k+1}: ${c.name}`.slice(0,30),x0+4,y+16);y+=26;
   ctx.fillStyle="#ddd";ctx.font="11px sans-serif";ctx.fillText(c.title.split(": ").slice(1).join(": ").slice(0,36),x0+4,y+10);y+=16;
   ctx.fillText((c.remark.split("\n")[0]||"").slice(0,40),x0+4,y+10);y+=14;
   for(const ym of c.ym){const mo=data.months[ym],cells=new Map(c.cells.map(x=>[x.date+"|"+x.g,x]));
    ctx.fillStyle="#1f2a44";ctx.fillRect(x0,y,W,24);ctx.fillStyle="#ffc000";ctx.font="bold 14px sans-serif";ctx.fillText(mo.label.toUpperCase(),x0+6,y+17);y+=26;
    ctx.fillStyle="#00b0f0";ctx.fillRect(x0,y,W,22);ctx.fillStyle="#fff";ctx.font="bold 12px sans-serif";["Tarikh",...G].forEach((h,i)=>ctx.fillText(h,x0+(i?56+(i-1)*44+10:4),y+15));y+=22;
    for(const [iso,v] of mo.days){const d=+iso.slice(8),x=[0,1,2,3].map(g=>cells.get(iso+"|"+g));
     ctx.fillStyle="#111";ctx.fillRect(x0,y,W,H);ctx.fillStyle="#00b0f0";ctx.font="bold 12px sans-serif";ctx.fillText(d+" "+MN[+iso.slice(5,7)-1],x0+3,y+15);
     for(let g=0;g<4;g++){const cx=x0+56+g*44,xx=x[g];if(xx){ctx.fillStyle=xx.kind==="light"?lighten(c.color):"#"+c.color;ctx.fillRect(cx,y,43,H-1)}
      ctx.fillStyle=xx?"#000":"#fff";ctx.font="bold 13px sans-serif";const txt=xx&&xx.text?xx.text:(v?p2(v[g]):"");ctx.fillText(txt,cx+12,y+15);
      if(xx&&xx.kind==="pass"){ctx.strokeStyle="#000";ctx.lineWidth=3;ctx.strokeRect(cx+1.5,y+1.5,40,H-4)}}
     ctx.strokeStyle="#444";ctx.lineWidth=1;ctx.strokeRect(x0,y,W,H);y+=H}
    y+=10}});
  cv.toBlob(b=>{const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download=`Pattern_${key}.png`;a.click()})}
 async function loadCopies(key,box){
  box.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Copy bana raha hai..."));
  try{const d=await api("GET",`/scanner/months?key=${key}&scope=${mscope}`);
   box.replaceChildren(el("p",{class:"mut small"},`${d.shown} copy dikh rahi hain${d.capped?` (kul ${d.total}, pehli ${d.shown} dikhayi)`:""}. Har copy me ek hi pattern, alag rang; rang par kaala ank. Tarikh, mahina aur saal upar likha hai.`),
    d.copies.length?el("div",{class:"row"},el("button",{class:"b g sm",on:{click:()=>drawPng(d,key)}},"Image download (PNG, saari copy ek image me)")):null,
    d.copies.length?copiesView(d):el("p",{class:"mut"},"Abhi koi pattern nahi chal raha."))}
  catch(e){box.replaceChildren(el("div",{class:"warn"},e.message))}}

 /* har pattern type ke upar: aaj ka batch ginti, bina dekhe filter, sab dekh liya, sab download */
 function bar(key,all){
  const n=all.length,seen=all.filter(i=>SX.reviewed(i.id)).length;
  const dl=f=>el("a",{href:`/api/scanner/bulk?key=${encodeURIComponent(key)}&fmt=${f[0]}&status=${filter==="aaj"?"aaj":"all"}`,class:"dlx"},el("button",{class:"b g sm"},f[1]));
  return el("div",{class:"batchbar"},
   el("div",{class:"row"},el("b",{},`Aaj ka batch: ${n} pattern | ${seen} dekhe`)),
   el("p",{class:"mut small",style:"margin:2px 0"},"Aaj ka naya batch: kal ke dekhe hue ginti me nahi"),
   el("div",{class:"row"},
    el("button",{class:"b g sm"+(unseen[key]?" on":""),on:{click:()=>{unseen[key]=!unseen[key];draw()}}},unseen[key]?"Sab dikhao":"Sirf bina dekhe"),
    el("button",{class:"b sm",on:{click:async()=>{if(!n)return;try{await SX.mark(all.map(i=>i.id),true);toast("Sab dekh liya");draw()}catch(e){toast(e.message)}}}},"Sab dekh liya")),
   el("div",{class:"row"},el("span",{class:"small"},"Sab download:"),[["pdf","PDF"],["jpg","JPG"],["xlsx","Excel"]].map(dl)))}
 function showDetail(){
  if(!sel){detail.replaceChildren();return}
  const p=rep.patterns.find(x=>x.key===sel),ix=idx.find(x=>x.key===sel)||{};
  const items=p?p.items:[],rd=el("pre",{class:"readme small",style:"display:none"},ix.readme||"(README nahi mila)");
  const rb=el("button",{class:"b g sm",on:{click:()=>{const on=rd.style.display==="none";rd.style.display=on?"block":"none";rb.textContent=on?"README band karo":"README padho (kaise bana)"}}},"README padho (kaise bana)");
  const copies=el("div"),sc=el("select",{on:{change:()=>{mscope=sc.value;loadCopies(sel,copies)}}},[["recent","Abhi chalte hue (aaj + pichle 3 din)"],["month","Is mahine ke saare (max 24)"]].map(([v,t])=>el("option",{value:v,selected:v===mscope},t)));
  const hasCopies=(sel==="family"||sel==="copy");
  detail.replaceChildren(el("div",{class:"card"},
   el("h2",{},`${ix.id||""} ${ix.naam||sel} `,el("span",{class:"pill "+(ix.pushti?"g":"o")},ix.pushti?"aap ki pushti ho chuki":"pushti baaki (abhi seekh rahe hain)")),
   el("p",{class:"mut"},ix.about||""),p?el("p",{class:"small"},p.summary):null,
   el("p",{class:"mut small"},"Is README me kuch galat lage to mujhe batao, main README sahi kar dunga."),
   el("div",{class:"row"},rb,el("button",{class:"b g sm",on:{click:()=>{sel=null;draw()}}},"Sab pattern dikhao")),rd),
   sel==="baar"?el("div",{class:"card"},el("p",{},"Ye ek hint (highlight) wala tool hai. Aaj ki List tab ke 'Baar Filter' card me apni jodi daalo, aaj ke baar ki tokri wale number narangi me chamkenge."),el("div",{class:"row"},el("button",{class:"b sm",on:{click:()=>go("baar")}},"Din (Baar) tab kholo: saatho din ki list"),el("button",{class:"b g sm",on:{click:()=>go("aaj")}},"Aaj ki List (Baar Filter)"))):null,
   hasCopies?el("div",{class:"card"},el("h2",{},"Mahine ki sheet ki copy ",el("span",{class:"sub"},"(har copy me ek pattern)")),el("div",{class:"row"},el("span",{},"Dikhao:"),sc),copies):null,
   p?el("div",{class:"card"},el("h2",{},`${ix.naam||sel}: abhi ke pattern (${items.length})`),items.length?[bar(sel,items),...items.map((x,i)=>card(x,i))]:el("p",{class:"mut"},"Abhi kuch nahi bana.")):null);
  if(hasCopies)loadCopies(sel,copies)}
 function drawIdx(){
  idxBox.replaceChildren(el("div",{class:"card"},el("h2",{},"Pattern Index ",el("span",{class:"sub"},"(naam par click karo)")),
   el("p",{class:"mut small"},"Har pattern ka apna naam aur README. Naam par click karo to wo pattern jitne abhi chal rahe hain sab dikhenge, aur ek mahine me kai hon to alag-alag copy me alag rang se."),
   idx.map(x=>el("button",{class:"idxrow"+(sel===x.key?" on":""),on:{click:()=>{sel=x.key;draw();detail.scrollIntoView&&detail.scrollIntoView({behavior:"smooth"})}}},
    el("b",{},`${x.id} ${x.naam}`)," ",el("span",{class:"pill "+(x.pushti?"g":"o")},x.pushti?"pushti ho chuki":"pushti baaki"),
    x.key!=="baar"?el("span",{class:"mut small"},`  ${x.count} chal rahe, aaj ${x.aaj}`):null,el("div",{class:"mut small"},x.about)))))}
 function draw(){
  if(!rep)return;
  const nA=rep.patterns.reduce((a,p)=>a+p.items.filter(i=>i.status==="aaj").length,0),nAll=rep.patterns.reduce((a,p)=>a+p.items.length,0);
  info.textContent=`Kul ${nAll} pattern dikh rahe hain, unme ${nA} aaj ban rahe hain (3rd step aaj). `+`Aakhri line: ${dm(rep.asof)} | Aaj khelne ki tarikh: ${dm(rep.play_date)} | script chali: ${istm(rep.time)} (${rep.seconds} sec)`;
  errBox.replaceChildren(...(rep.errors.length?[el("div",{class:"warn"},el("b",{},`Script me ${rep.errors.length} galti:`),rep.errors.map(e=>el("div",{style:"margin-top:6px"},el("b",{},e.pattern+": "),e.error,el("pre",{class:"small",style:"white-space:pre-wrap"},e.trace))))]:[el("p",{class:"ok small"},"Script me koi galti nahi.")]));
  drawIdx();showDetail();
  list.replaceChildren(...(sel?[]:rep.patterns.map(p=>{
   let items=p.items.map((x,i)=>[x,i]);if(filter==="aaj")items=items.filter(([i])=>i.status==="aaj");if(filter==="strong")items=items.filter(([i])=>i.strength==="mazboot"||i.strength==="theek");
   if(unseen[p.key])items=items.filter(([i])=>!SX.reviewed(i.id));
   return el("div",{class:"card"},el("h2",{},`${p.id} ${p.naam} `,el("span",{class:"pill "+(p.pushti?"g":"o")},p.pushti?"aap ki pushti ho chuki":"pushti baaki (abhi seekh rahe hain)")),el("p",{class:"mut small"},p.about),el("p",{class:"small"},p.summary),
    bar(p.key,p.items),items.length?items.map(([x,i])=>card(x,i)):el("p",{class:"mut"},filter==="all"&&!unseen[p.key]?"Abhi kuch nahi bana.":"Is filter me kuch nahi."))})))}
 m.append(el("div",{class:"card"},el("h2",{},"Pattern Scan ",el("span",{class:"sub"},"(sikhaye hue pattern aaj kya bana rahe hain)")),
  el("p",{class:"mut"},"Har sikhaya hua pattern roz subah data aate hi apne aap chalta hai. Har pattern ko apna naam diya hai (jaise Naksha-Hathi-44) taaki mix na ho. 'Kholo' dabao to saaf rang me chart dikhega, 'Excel download' se Excel aayega. 'Mazboot' tabhi likha jata hai jab milan random se bhi zyada ho; zyadatar abhi 'kamzor' hi nikalte hain."),
  el("div",{class:"row"},runBtn,el("span",{},"Dikhao:"),fsel),info,errBox),idxBox,detail,list);
 try{plays=await api("GET","/scanner/plays")}catch(e){plays={}}
 try{idx=await api("GET","/patterns/index")}catch(e){idx=[]}
 await SX.load();
 try{rep=await api("GET","/scanner");draw()}catch(e){errBox.replaceChildren(el("div",{class:"warn"},"Load nahi hua: "+e.message))}
};
})();
