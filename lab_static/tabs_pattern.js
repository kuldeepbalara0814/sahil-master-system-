"use strict";
/* PATTERN WINDOW: mahine upar-niche jude, gap ke rang, haath se rang bharo, save / mitao */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],DAY=["Ravi","Som","Mangal","Budh","Guru","Shukra","Shani"];
const GC={1:"FFD740",2:"FF5252",3:"FF9800",4:"E040FB",5:"1DE9B6",6:"40C4FF",7:"C6FF00",8:"7C4DFF",9:"FF80AB",10:"B0BEC5"};
const PAL=["FF9800","E040FB","1DE9B6","FF5252","C6FF00","40C4FF","FFD740","7C4DFF"];
const dm=s=>{const [y,m,d]=s.split("-").map(Number);return d+" "+MN[m-1]};
const lsGet=k=>{try{return localStorage.getItem(k)}catch(e){return null}},lsSet=(k,v)=>{try{v==null?localStorage.removeItem(k):localStorage.setItem(k,v)}catch(e){}};

tabs.pattern=async function(m){
 let layout=lsGet("playout")||"side",from=null,n=3,showAuto=true,gdays=15,tool=PAL[0],cells={},boardId=null,dirty=false,boards=[],data=null;
 const gset=new Set([3,4,5,6,7]);
 const key=()=>"pdraft:"+(from||"last")+":"+n;
 const wrap=el("div",{class:"sheetwrap pat"}),info=el("p",{class:"mut small"}),legend=el("div",{class:"row",style:"gap:8px"}),tbl=el("div",{class:"tw"});
 const nameIn=el("input",{type:"text",placeholder:"Pattern ka naam",maxlength:60,style:"width:200px"}),boardSel=el("select",{});
 const dirtyEl=el("span",{class:"pill m",style:"display:none"},"bina save");
 const setDirty=v=>{dirty=v;dirtyEl.style.display=v?"inline-block":"none"};
 const draftSave=()=>{lsSet(key(),Object.keys(cells).length?JSON.stringify({cells,boardId,name:nameIn.value}):null)};
 const q=()=>`from=${from||""}&months=${n}`+(showAuto&&gset.size?`&gaps=${[...gset].sort((a,b)=>a-b).join(",")}&days=${gdays}`:"");
 const colorOf=(k)=>cells[k];

 async function load(first){
  tbl.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load ho raha hai..."));
  try{data=await api("GET","/pattern/sheet?"+q())}catch(e){tbl.replaceChildren(el("div",{class:"warn"},e.message));return}
  from=data.from;
  if(first!==false){try{const d=JSON.parse(lsGet(key())||"null");if(d&&d.cells){cells=d.cells;boardId=d.boardId||null;nameIn.value=d.name||"";setDirty(true)}}catch(e){}}
  draw();
 }
 function draw(){
  const mk=new Map();for(const x of data.marks||[]){const k=x.date+"|"+x.g;(mk.get(k)||mk.set(k,[]).get(k)).push(x)}
  let firstMark=null;
  const cell=(iso,g,v)=>{
   const k=iso+"|"+g,ms=mk.get(k),a=ms&&ms[ms.length-1];
   const td=el("td",{class:"c"+(a?" auto "+a.kind:"")},a&&a.kind==="due"?a.text:(v?p2(v[g]):""));
   td.dataset.k=k;
   if(a){td.style.background="#"+a.color;td.style.color="#000";td.title=ms.map(x=>x.tip).join("\n");if(a.kind==="pass")td.style.outline="3px solid #fff";if(!firstMark)firstMark=td}
   if(cells[k]){td.style.background="#"+cells[k];td.style.color="#000";td.classList.add("paint")}
   td.onclick=()=>{
    if(tool==="x"||cells[k]===tool){delete cells[k]}else{cells[k]=tool}
    const c=cells[k];
    if(c){td.style.background="#"+c;td.style.color="#000";td.classList.add("paint")}
    else{td.classList.remove("paint");const a2=ms&&ms[ms.length-1];if(a2){td.style.background="#"+a2.color;td.style.color="#000"}else{td.style.background="";td.style.color=""}}
    setDirty(true);draftSave()};
   return td};
  const t=el("table",{class:"sheet pt"+(layout==="side"?" side":"")}),th=el("thead"),tb=el("tbody");
  if(layout==="side"){
   const byM=new Map();for(const [iso,v] of data.days){const ym=iso.slice(0,7);(byM.get(ym)||byM.set(ym,new Map()).get(ym)).set(+iso.slice(8),[iso,v])}
   const yms=[...byM.keys()];
   th.append(el("tr",{},el("th",{class:"d",rowspan:2},"Date"),yms.map(ym=>{const [y,mo]=ym.split("-").map(Number);return el("th",{class:"mh mb mr",colspan:4},`${MN[mo-1]}-${String(y).slice(2)}`)})));
   th.append(el("tr",{},yms.flatMap(()=>["FB","GB","GL","DS"].map((g,j)=>el("th",{class:"sh"+(j==0?" mb":"")+(j==3?" mr":"")},g)))));
   for(let d=1;d<=31;d++){
    tb.append(el("tr",{class:"dr"},el("td",{class:"d"},d),yms.flatMap(ym=>{const e=byM.get(ym).get(d);
     return [0,1,2,3].map(g=>{if(!e){const td=el("td",{class:"x"+(g==0?" mb":"")+(g==3?" mr":"")},"");return td}
      const td=cell(e[0],g,e[1]);if(g==0)td.classList.add("mb");if(g==3)td.classList.add("mr");return td})})))}
  }else{
   th.append(el("tr",{},["Tarikh","Din","FB","GB","GL","DS"].map((h,i)=>el("th",{class:i<2?"d":"sh"},h))));
   let cur="";
   for(const [iso,v] of data.days){
    const [y,mo,d]=iso.split("-").map(Number),ym=iso.slice(0,7);
    if(ym!==cur){cur=ym;tb.append(el("tr",{class:"mrow"},el("td",{colspan:6},`${MN[mo-1].toUpperCase()} ${y}`)))}
    const tr=el("tr",{class:"dr"+(new Date(y,mo-1,d).getDay()===0?" sun":"")},el("td",{class:"d"},d+" "+MN[mo-1]),el("td",{class:"d dn"},DAY[new Date(y,mo-1,d).getDay()]));
    for(let g=0;g<4;g++)tr.append(cell(iso,g,v));
    tb.append(tr)}}
  t.append(th,tb);wrap.replaceChildren(t);tbl.replaceChildren(wrap);
  const nch=data.gap?data.gap.chains.length:0;
  info.textContent=`${data.days.length} din, ${data.from} se ${n} mahine.`+(data.gap?` Gap nishan: ${dm(data.gap.start)} se ${dm(data.gap.end)} tak ${nch} chain.`:"")+` Aakhri result: ${dm(data.last)}.`;
  legend.replaceChildren(...(data.gap?Object.entries(data.gap.legend).map(([g,c])=>el("span",{class:"chk"},el("span",{class:"dot",style:"background:#"+c}),`${g} din gap`)):[]),
   ...(data.gap?[el("span",{class:"mut small"},"'NN?' = us din 3rd step aane wala, moti safed border = 3rd step aa gaya (pass)")]:[]));
  setTimeout(()=>{const tgt=firstMark||wrap.querySelector("tbody tr:last-child");if(!tgt)return;
   const row=tgt.tagName==="TD"?tgt.parentNode:tgt;wrap.scrollTop=Math.max(0,row.offsetTop-wrap.clientHeight/3);
   if(layout==="side"&&firstMark)wrap.scrollLeft=Math.max(0,firstMark.offsetLeft-80)},50);
 }
 const refresh=()=>load(false);
 async function loadBoards(){try{boards=await api("GET","/pattern/boards")}catch(e){boards=[]}
  boardSel.replaceChildren(el("option",{value:""},boards.length?"— save kiya hua pattern kholo —":"(abhi koi save nahi)"),...boards.map(b=>el("option",{value:b.id},`${b.name} (${b.from}, ${b.months} mahine, ${Object.keys(b.cells).length} rang)`)))}
 boardSel.onchange=()=>{const b=boards.find(x=>String(x.id)===boardSel.value);if(!b)return;from=b.from;n=b.months;cells={...b.cells};boardId=b.id;nameIn.value=b.name;setDirty(false);lsSet(key(),null);load(false)};
 async function save(){
  if(!Object.keys(cells).length)return toast("Pehle kuch cell me rang bharo");
  try{const r=await api("POST","/pattern/save",{id:boardId,name:nameIn.value||"Mera pattern",from,months:n,cells});boardId=r.id;setDirty(false);lsSet(key(),null);toast("Pattern save ho gaya");await loadBoards();boardSel.value=String(boardId)}catch(e){toast(e.message)}}
 async function del(){
  if(!boardId||!boards.some(b=>b.id===boardId))return toast("Ye pattern save nahi hai (sirf screen par hai). 'Sab saaf karo' dabao.");
  if(!confirm("Save kiya hua pattern hamesha ke liye hata dun?"))return;
  try{await api("POST","/pattern/delete",{id:boardId});boardId=null;cells={};nameIn.value="";setDirty(false);lsSet(key(),null);toast("Pattern hata diya");await loadBoards();draw()}catch(e){toast(e.message)}}
 function clearAll(){if(Object.keys(cells).length&&!confirm("Saare rang hata kar pehle jaisa kar dun? (save kiya hua pattern nahi hatega)"))return;
  cells={};boardId=null;nameIn.value="";boardSel.value="";setDirty(false);lsSet(key(),null);draw()}

 const lay=el("div",{class:"row"},el("span",{},"Dikhane ka tareeka:"),
  [["side","Excel jaisa (mahine side-by-side)"],["long","Lamba (mahine upar-niche)"]].map(([k,t])=>{const b=el("button",{class:"b g sm"+(k===layout?" on":""),on:{click:()=>{layout=k;lsSet("playout",k);lay.querySelectorAll("button").forEach(x=>x.classList.toggle("on",x.dataset.k===k));draw()}}},t);b.dataset.k=k;return b}));
 const mi=el("input",{type:"month",min:"2013-01",value:""});
 mi.onchange=()=>{if(mi.value){from=mi.value;cells=cells;load(true)}};
 const nsel=el("select",{},[1,2,3,4,5,6,9,12].map(v=>el("option",{value:v,selected:v===n},v+" mahine")));
 nsel.onchange=()=>{n=+nsel.value;load(true)};
 const swatch=(c)=>{const b=el("button",{class:"sw"+(c===tool?" on":""),style:"background:#"+c,title:"Ye rang bharo",on:{click:()=>{tool=c;sync()}}});b.dataset.c=c;return b};
 const eraser=el("button",{class:"b g sm",on:{click:()=>{tool="x";sync()}}},"Mitao (default)");
 const sw=PAL.map(swatch);
 const sync=()=>{sw.forEach(b=>b.classList.toggle("on",b.dataset.c===tool));eraser.classList.toggle("on",tool==="x")};
 const gchk=Object.keys(GC).map(Number).map(g=>{const cb=el("input",{type:"checkbox",checked:gset.has(g),on:{change:()=>{cb.checked?gset.add(g):gset.delete(g);refresh()}}});
  return el("label",{class:"chk"},cb,el("span",{class:"dot",style:"background:#"+GC[g]}),String(g))});
 const autoCb=el("input",{type:"checkbox",checked:true,on:{change:()=>{showAuto=autoCb.checked;refresh()}}});
 const dIn=el("input",{type:"number",min:3,max:400,value:gdays,style:"width:80px"});
 dIn.onchange=()=>{gdays=Math.max(3,Math.min(400,+dIn.value||15));dIn.value=gdays;refresh()};

 m.append(
  el("div",{class:"card"},el("h2",{},"Pattern Window ",el("span",{class:"sub"},"(rang bharo, save karo, Excel ki zarurat nahi)")),
   el("p",{class:"mut"},"Mahine ek ke neeche ek jude hain (continuous), isliye gap seedha ginti se dikhta hai. Neeche kisi bhi cell par dabao to chuna hua rang bhar jaata hai, dobara dabao to hat jaata hai."),
   el("div",{class:"row"},el("span",{},"Mahina chuno:"),mi,el("span",{},"kitne jodne:"),nsel),
   lay,
   el("div",{class:"row"},el("span",{},"Jaldi:"),[1,2,3,4,6].map(k=>el("button",{class:"b g sm",on:{click:()=>{from=null;n=k;nsel.value=k;mi.value="";cells={};boardId=null;nameIn.value="";setDirty(false);load(true)}}},`Pichle ${k} mahine`)))),
  el("div",{class:"card"},el("h3",{},"Gap ke nishan (apne aap)"),
   el("div",{class:"row"},el("label",{class:"chk"},autoCb,"Dikhao"),el("span",{},"Gap (din):"),gchk),
   el("div",{class:"row"},el("span",{},"Pichle kitne din ke step:"),dIn,[12,15,20,30,60,90].map(k=>el("button",{class:"b g sm",on:{click:()=>{gdays=k;dIn.value=k;refresh()}}},String(k)))),legend),
  el("div",{class:"card"},el("h3",{},"Apna rang bharo"),
   el("div",{class:"row"},sw,eraser,el("button",{class:"b r sm",on:{click:clearAll}},"Sab saaf karo"),dirtyEl),
   el("div",{class:"row"},nameIn,el("button",{class:"b",on:{click:save}},"Save"),boardSel,el("button",{class:"b g sm",on:{click:del}},"Save kiya hua hatao"))),
  info,tbl);
 await loadBoards();await load(true);
};
})();
