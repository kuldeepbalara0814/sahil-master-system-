"use strict";
/* PATTERN SCAN: sikhaye hue pattern roz apne aap chalte hain; aaj kya ban raha hai, saaf rang me, Excel download */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const dm=s=>{const [y,m,d]=s.split("-").map(Number);return d+" "+MN[m-1]};
const G=["FB","GB","GL","DS"];
const ST={aaj:["o","Aaj ban raha"],pass:["g","PASS"],fail:["r","FAIL"],dekho:["m","dekho"]};
const SR={mazboot:["g","mazboot"],theek:["y","theek"],kamzor:["m","kamzor (random jaisa)"],info:["m","jaankari"]};

function chart(v){
 const t=el("table",{class:"sheet scn"}),th=el("thead"),tb=el("tbody");
 th.append(el("tr",{},v.blocks.map(b=>el("th",{class:"ttl2",colspan:5},b.label))));
 th.append(el("tr",{},v.blocks.flatMap(()=>["Tarikh",...G].map((h,i)=>el("th",{class:i==0?"d":"sh"},h)))));
 const n=Math.max(...v.blocks.map(b=>b.rows.length));
 for(let i=0;i<n;i++){
  tb.append(el("tr",{},v.blocks.flatMap(b=>{const r=b.rows[i];if(!r)return Array(5).fill(el("td",{}));
   const d=el("td",{class:"d"},r.date&&r.date!=="aage"?dm(r.date):(r.date==="aage"?"aage":""));
   return [d,...[0,1,2,3].map(g=>{const txt=r.txt[g]||(r.v?p2(r.v[g]):"");const td=el("td",{class:"c"+(r.kind[g]?" "+r.kind[g]:"")},txt);
    if(r.c[g]){td.style.background="#"+r.c[g];td.style.color="#000"}if(r.kind[g]==="pass")td.style.outline="3px solid #000";if(r.kind[g]==="light")td.style.fontStyle="italic";return td})]})))}
 t.append(th,tb);return el("div",{},el("p",{class:"mut small"},v.note),el("div",{class:"sheetwrap",style:"max-height:60vh"},t));
}

tabs.scan=async function(m){
 let rep=null,filter="all",plays={};
 const info=el("p",{class:"mut small"}),errBox=el("div"),list=el("div"),runBtn=el("button",{class:"b"},"Script abhi chalao (manual)");
 const fsel=el("select",{on:{change:()=>{filter=fsel.value;draw()}}},[["all","Sab dikhao"],["aaj","Sirf aaj ke andaze wale"],["strong","Sirf mazboot/theek"]].map(([v,t])=>el("option",{value:v},t)));
 async function run(){
  runBtn.disabled=true;runBtn.textContent="Chal rahi hai...";
  try{rep=await api("POST","/scanner/run",{});toast(rep.errors.length?"Script chali par galti aayi (neeche dekho)":"Script poori chali, sab theek");draw()}
  catch(e){errBox.replaceChildren(el("div",{class:"warn"},"Script chali hi nahi: "+e.message))}
  finally{runBtn.disabled=false;runBtn.textContent="Script abhi chalao (manual)"}}
 runBtn.onclick=run;
 function card(it){
  const view=el("div"),st=ST[it.status]||ST.dekho,sr=SR[it.strength]||SR.info;
  const open=el("button",{class:"b g sm"},"Kholo (rang me dekho)");let on=false;
  open.onclick=async()=>{on=!on;if(!on){view.replaceChildren();open.textContent="Kholo (rang me dekho)";return}
   open.textContent="Band karo";view.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load..."));
   try{view.replaceChildren(chart(await api("GET","/scanner/view?id="+encodeURIComponent(it.id))))}catch(e){view.replaceChildren(el("div",{class:"warn"},e.message))}};
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
  return el("div",{class:"card flat scard"},
   el("div",{class:"row",style:"justify-content:space-between"},el("h3",{style:"margin:0"},it.name),el("span",{},el("span",{class:"pill "+st[0]},st[1])," ",el("span",{class:"pill "+sr[0]},sr[1]))),
   el("div",{class:"b"},it.title),it.lines.map(l=>el("p",{class:"mut small",style:"margin:3px 0"},l)),
   it.target?el("p",{class:"tgt"},`Aaj ${dm(it.target.date)}: ${it.target.games} me `,el("b",{},it.target.numbers.map(p2).join(" ")),it.kind==="copy"?" (set ka koi bhi)":" (andaza)"):null,
   el("div",{class:"row"},open,pb,el("a",{href:"/api/scanner/xlsx?id="+encodeURIComponent(it.id)},el("button",{class:"b g sm"},"Excel download"))),saved,panel,view)}
 function draw(){
  if(!rep)return;
  const nA=rep.patterns.reduce((a,p)=>a+p.items.filter(i=>i.status==="aaj").length,0),nAll=rep.patterns.reduce((a,p)=>a+p.items.length,0);
  info.textContent=`Kul ${nAll} pattern dikh rahe hain, unme ${nA} aaj ban rahe hain (3rd step aaj). `+`Aakhri line: ${dm(rep.asof)} | Aaj khelne ki tarikh: ${dm(rep.play_date)} | script chali: ${rep.time.replace("T"," ")} (${rep.seconds} sec)`;
  errBox.replaceChildren(...(rep.errors.length?[el("div",{class:"warn"},el("b",{},`Script me ${rep.errors.length} galti:`),rep.errors.map(e=>el("div",{style:"margin-top:6px"},el("b",{},e.pattern+": "),e.error,el("pre",{class:"small",style:"white-space:pre-wrap"},e.trace))))]:[el("p",{class:"ok small"},"Script me koi galti nahi.")]));
  list.replaceChildren(...rep.patterns.map(p=>{
   let items=p.items;if(filter==="aaj")items=items.filter(i=>i.status==="aaj");if(filter==="strong")items=items.filter(i=>i.strength==="mazboot"||i.strength==="theek");
   return el("div",{class:"card"},el("h2",{},`${p.id} ${p.naam} `,el("span",{class:"pill "+(p.pushti?"g":"o")},p.pushti?"aap ki pushti ho chuki":"pushti baaki (abhi seekh rahe hain)")),el("p",{class:"mut small"},p.about),el("p",{class:"small"},p.summary),
    items.length?items.map(card):el("p",{class:"mut"},filter==="all"?"Abhi kuch nahi bana.":"Is filter me kuch nahi."))}))}
 m.append(el("div",{class:"card"},el("h2",{},"Pattern Scan ",el("span",{class:"sub"},"(sikhaye hue pattern aaj kya bana rahe hain)")),
  el("p",{class:"mut"},"Har sikhaya hua pattern roz subah data aate hi apne aap chalta hai. Har pattern ko apna naam diya hai (jaise Naksha-Hathi-44) taaki mix na ho. 'Kholo' dabao to saaf rang me chart dikhega, 'Excel download' se Excel aayega. 'Mazboot' tabhi likha jata hai jab milan random se bhi zyada ho; zyadatar abhi 'kamzor' hi nikalte hain."),
  el("div",{class:"row"},runBtn,el("span",{},"Dikhao:"),fsel),info,errBox),list);
 try{plays=await api("GET","/scanner/plays")}catch(e){plays={}}
 try{rep=await api("GET","/scanner");draw()}catch(e){errBox.replaceChildren(el("div",{class:"warn"},"Load nahi hua: "+e.message))}
};
})();
