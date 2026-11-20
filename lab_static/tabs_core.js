"use strict";
Object.assign(tabs,{
/* ---------------- 1. DOST KHOJO ---------------- */
async dost(m){
 const inp=el("input",{id:"x",type:"number",min:"0",max:"99",inputmode:"numeric",value:"30",style:"width:110px;font-size:26px;font-weight:800;text-align:center"});
 const out=el("div");
 const go=async()=>{const x=parseInt(inp.value,10);if(!(x>=0&&x<=99))return toast("0 se 99 ka number likho");
  out.replaceChildren(el("p",{class:"mut"},"Dhundh raha hai..."));
  try{const t=await api("GET","/friends/"+x);const d=await api("GET","/drift");render(t,d)}catch(e){out.replaceChildren(el("div",{class:"warn"},e.message))}};
 inp.addEventListener("keydown",e=>{if(e.key==="Enter")go()});
 function col(name,title,t){
  const f=t.friends[name];const c=el("div",{class:"card",style:"margin:0"},el("h3",{},title),el("div",{class:"mut",style:"font-size:12px"},(t.since[name]?`${t.since[name]} se`:"2013 se")+` | ${p2(t.number)} ${t.seen[name]} baar aaya`));
  if(!f.length)c.append(el("p",{class:"mut"},"Is samay me abhi koi dost nahi mila."));
  f.forEach((x,i)=>{const r=el("div",{class:"fr"},chip(x.n,x.tier),el("div",{style:"flex:1"},el("b",{},x.together+" baar"),el("span",{class:"mut"},"  "+pct(x.pct)+" (random "+pct(x.random_pct)+")")));
   if(name!=="poora"){const tag=x.change==="naya"?el("span",{class:"tag new"},"naya"):x.change==="upar"?el("span",{class:"tag up"},"▲ upar"):x.change==="neeche"?el("span",{class:"tag down"},"▼ neeche"):el("span",{class:"tag"},"wahi");r.append(tag);
    if(x.boost)r.append(el("span",{class:"tag"},"x"+x.boost));if(x.few)r.append(el("span",{class:"tag few"},"kam data"))}
   c.append(r)});return c}
 function render(t,drift){
  out.replaceChildren();
  const tp=n=>t.friends[n].length?p2(t.friends[n][0].n):"-";
  out.append(el("div",{class:"card"},el("h2",{},`${p2(t.number)} ke dost - ek nazar me`),
   el("div",{class:"row"},el("div",{},el("div",{class:"mut"},"Poora (13 saal)"),chip(t.friends.poora[0]?t.friends.poora[0].n:0,"green","big")),
    el("div",{},el("div",{class:"mut"},"Pichle 3 mahine"),t.friends.last3m[0]?chip(t.friends.last3m[0].n,"yellow","big"):el("span",{class:"mut"},"-")),
    el("div",{},el("div",{class:"mut"},"Is mahina"),t.friends.month[0]?chip(t.friends.month[0].n,"orange","big"):el("span",{class:"mut"},"-"))),
   (tp("poora")!==tp("last3m")||tp("poora")!==tp("month"))?el("p",{},"⚠ Sabse bada dost badal raha hai: pehle ",el("b",{},tp("poora")),", ab (3 mahine) ",el("b",{},tp("last3m")),", is mahine ",el("b",{},tp("month")),". Recent samay me data kam hota hai, isliye ise pakka mat maano."):el("p",{},"✔ Sabse bada dost teeno samay me wahi hai."),
   LEGEND()));
  out.append(el("div",{class:"grid3"},col("poora","Poora (sab saal)",t),col("last3m","Pichle 3 mahine (is mahine samet)",t),col("month","Is mahina (chal raha)",t)));
  const mine=[];for(const e of drift)for(const c of e.changes)if(c.number===t.number)mine.push([e.asof,c]);
  const pn={poora:"poora",last3m:"3 mahine",month:"is mahine"};
  out.append(el("div",{class:"card"},el("h2",{},"Kya badla (drift) - aap ka sawal: pehle 93 tha ab 94?"),
   mine.length?el("ul",{class:"g"},mine.slice(0,10).map(([d,c])=>el("li",{},`${d}: ${p2(c.number)} par (${pn[c.period]}) sabse bada dost ${p2(c.old)} se ${p2(c.new)} ho gaya`))):el("p",{class:"mut"},"Is number ke sabse bade dost me abhi tak koi badlaav darj nahi hua. Roz subah ka update ye apne aap jodta hai."),
   el("h3",{},"Aaj-kal ke saare badlaav"),drift.length?el("ul",{class:"g"},drift.slice(0,3).flatMap(e=>e.changes.filter(c=>c.period!=="poora").slice(0,6).map(c=>el("li",{},`${e.asof}: ${p2(c.number)} (${pn[c.period]}): ${p2(c.old)} -> ${p2(c.new)}`)))):el("p",{class:"mut"},"Abhi koi nahi.")))}
 m.append(el("div",{class:"card"},el("h2",{},"Dost Khojo"),el("p",{class:"mut"},"Number likho: uske sabse zyada saath aane wale 10 number 3 samay ke hisaab se dikhenge."),el("div",{class:"row"},inp,el("button",{class:"b",on:{click:go}},"Dost dikhao"))),out);go()},

/* ---------------- 2. AAJ KI LIST ---------------- */
async aaj(m){
 const known=[el("input",{id:"k0",type:"number",min:"0",max:"99",placeholder:"FB",style:"width:84px"}),el("input",{id:"k1",type:"number",min:"0",max:"99",placeholder:"GB",style:"width:84px"}),el("input",{id:"k2",type:"number",min:"0",max:"99",placeholder:"GL",style:"width:84px"})];
 const stake=el("select",{},[5,10,15,20,25,30,40,50].map(v=>el("option",{value:v},v+" Rs")));
 const out=el("div");
 const vals=()=>{const v=[];for(const k of known){if(k.value==="")break;v.push(parseInt(k.value,10))}return v};
 async function load(){
  const kv=vals();const t=await api("GET","/today?known="+kv.join(","));out.replaceChildren();
  out.append(el("div",{class:"card"},el("h2",{},"Khelne ki tarikh: "+t.play_date),el("div",{class:"mut"},"Pichli line ("+t.last_line.date+"):  "+Object.entries(t.last_line.results).map(([g,v])=>GN[g]+" "+p2(v)).join("   ")),
   el("h3",{},"SINGLE JODI  (kal ka GB number)"),el("div",{class:"row"},chip(t.single.number,"blue","big"),el("div",{},el("div",{},"Khelo: ",el("b",{},"FB, GL, DS")),el("div",{class:"mut"},"GB me nahi. Har bet 95 guna (40 se kam number)."),
   el("button",{class:"b",on:{click:()=>place({strategy:"manual",numbers:[t.single.number],games:t.single.games})}},"Paper bet: single jodi"))),
   el("p",{class:"warn"},"Ye paper trading hai (kalpnik paisa). Asar chhota hai aur ghat-badh sakta hai, pakka nahi.")));
  const g4=el("div",{class:"grid4"});
  ["FD","GB","GL","DS"].forEach((g,gi)=>{const seq=t.list10[g];const lst=seq||t.list10_static[g];
   g4.append(el("div",{class:"card",style:"margin:0"},el("h3",{},GN[g]+(seq?"  (aaj ke result dekh kar)":"  (subah wali)")),
    el("div",{class:"row"},lst.map(([n,s],i)=>el("span",{class:"chip "+tiers(i),title:"score "+s},p2(n)))),
    el("div",{class:"mut",style:"font-size:12px;margin-top:6px"},"Hara = top 3, peela = beech, narangi = baaki")))});
  out.append(el("div",{class:"card"},el("h2",{},"Har game ki 10 number ki list"),g4,LEGEND(),
   el("div",{class:"row",style:"margin-top:10px"},el("button",{class:"b",on:{click:()=>place({strategy:"auto"})}},"Subah ki saari paper bet lagao"),
    el("button",{class:"b g",on:{click:()=>place({strategy:"list10",known:vals()})}},"Agle game ki list ki bet (upar ke result ke baad)"))));
 }
 async function place(b){try{b.stake=parseInt(stake.value,10);const r=await api("POST","/paper/place",b);toast(`${r.added} nayi paper bet lagi (${r.play_date})`+(r.saved_to_github?" - GitHub par save":""))}catch(e){toast(e.message)}}
 known.forEach(k=>k.addEventListener("change",()=>load().catch(e=>toast(e.message))));
 m.append(el("div",{class:"card"},el("h2",{},"Aaj ki List"),el("p",{class:"mut"},"Aaj ke ab tak aaye result (FB, GB, GL) niche likho to baad ke game ki list unke hisaab se badal jayegi."),
  el("div",{class:"row"},el("span",{},"Aaj ke result:"),known,el("span",{},"Stake:"),stake)),out);
 await load()},

/* ---------------- 3. PAPER TRADING ---------------- */
async paper(m){
 const p=await api("GET","/paper");const names=p.strategies;
 m.append(el("div",{class:"card"},el("h2",{},"Paper Trading ",el("span",{class:"sub"},"(kalpnik paisa)")),el("p",{class:"mut"},"Shuruati kalpnik paisa: "+p.capital+" Rs. Koi asli paisa nahi. Bet ka result aate hi jeet/haar apne aap likh jaati hai."),
  Object.keys(p.summary).length?null:el("p",{},"Abhi koi bet nahi. 'Aaj ki List' tab se bet lagao.")));
 for(const [k,s] of Object.entries(p.summary)){
  const w=300,h=70;const cv=s.curve.map(c=>c.net);const mn=Math.min(0,...cv),mx=Math.max(0,...cv);
  const pts=cv.map((v,i)=>`${(i/(Math.max(1,cv.length-1)))*w},${h-((v-mn)/((mx-mn)||1))*h}`).join(" ");
  const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");svg.setAttribute("viewBox",`0 0 ${w} ${h}`);svg.setAttribute("width","100%");svg.setAttribute("height",h);
  const pl=document.createElementNS("http://www.w3.org/2000/svg","polyline");pl.setAttribute("points",pts);pl.setAttribute("fill","none");pl.setAttribute("stroke",s.net>=0?"#2e9e4f":"#d64545");pl.setAttribute("stroke-width","2");svg.append(pl);
  const mrows=Object.entries(s.months).sort().slice(-6).reverse();
  m.append(el("div",{class:"card"},el("h2",{},fb(names[k])),el("div",{class:"row"},
   el("div",{},el("div",{class:"mut"},"Bet"),el("b",{},s.bets+" (baaki "+s.pending+")")),el("div",{},el("div",{class:"mut"},"Jeet"),el("b",{},s.wins+" ("+pct(s.hit_pct,2)+")")),
   el("div",{},el("div",{class:"mut"},"Net"),el("b",{class:s.net>=0?"ok":"bad"},(s.net>=0?"+":"")+s.net+" Rs")),el("div",{},el("div",{class:"mut"},"ROI"),el("b",{class:s.roi>=0?"ok":"bad"},pct(s.roi))),
   el("div",{},el("div",{class:"mut"},"Ab ka paisa"),el("b",{},s.capital_now+" Rs")),el("div",{},el("div",{class:"mut"},"Sabse badi giraavat"),el("b",{},s.max_drawdown+" Rs"))),
   s.curve.length?svg:el("p",{class:"mut"},"Abhi settle hui bet nahi."),
   mrows.length?el("table",{},el("thead",{},el("tr",{},["Mahina","Bet","Jeet","Net"].map(x=>el("th",{},x)))),el("tbody",{},mrows.map(([mm,v])=>el("tr",{},el("td",{},mm),el("td",{},v.bets),el("td",{},v.wins),el("td",{class:v.net>=0?"ok":"bad"},v.net))))):null))}
 const num=el("input",{placeholder:"jaise 47, 74",style:"width:160px"});const games=["FD","GB","GL","DS"].map(g=>el("label",{class:"chk"},el("input",{type:"checkbox",value:g,checked:true})," "+GN[g]));
 const stake=el("select",{},[5,10,15,20,25,30,40,50].map(v=>el("option",{value:v},v+" Rs")));
 m.append(el("div",{class:"card"},el("h2",{},"Meri apni paper bet (aaj ke liye)"),el("div",{class:"row"},num,games,stake,el("button",{class:"b",on:{click:async()=>{
  const ns=num.value.split(/[ ,]+/).filter(Boolean).map(Number);const gs=games.map(l=>l.firstChild).filter(i=>i.checked).map(i=>i.value);
  try{const r=await api("POST","/paper/place",{strategy:"manual",numbers:ns,games:gs,stake:parseInt(stake.value,10)});toast(r.added+" bet lagi")}catch(e){toast(e.message)}}}},"Bet lagao"))));
 m.append(el("div",{class:"card"},el("h2",{},"Pichli bet"),el("table",{},el("thead",{},el("tr",{},["Tarikh","Game","Number","Stake","Result","Haal","Net"].map(x=>el("th",{},x)))),
  el("tbody",{},p.recent.map(b=>el("tr",{},el("td",{},b.date),el("td",{},GN[b.game]||b.game),el("td",{},p2(b.number)),el("td",{},b.stake),el("td",{},b.result===null?"-":p2(b.result)),
   el("td",{class:b.status==="win"?"ok":b.status==="loss"?"bad":"mut"},b.status==="win"?"JEET":b.status==="loss"?"haar":"baaki"),el("td",{class:b.net>0?"ok":b.net<0?"bad":""},b.net===null?"-":b.net)))))))},

/* ---------------- 4. MONITOR ---------------- */
async monitor(m){
 const d=await api("GET","/monitor");const nm={single:"Single jodi (FB+GL+DS)",list10s:"10 number list (subah wali)",list10:"10 number list (game se pehle)"};
 const pn={all:"Poora",y2016:"2016 se",last12m:"Pichle 12 mahine",last3m:"Pichle 3 mahine",last30d:"Pichle 30 din"};
 m.append(el("div",{class:"card"},el("h2",{},"Monitor: asar chal raha hai ya ghat gaya?"),el("p",{class:"mut"},`Hit % = 100 me kitni baar number aaya. Break-even ${pct(d.breakeven,2)} (95 guna par). Random = 1.00%. Data: ${d.asof} tak.`),
  d.alerts.length?el("div",{class:"warn"},d.alerts.map(a=>el("div",{},"⚠ "+fb(a)))):el("p",{class:"ok"},"✔ Abhi koi chetavani nahi."),
  el("p",{class:"legend mut"},el("span",{class:"st hara"},"hara")," break-even se 10% upar  ",el("span",{class:"st peela"},"peela")," aas-paas  ",el("span",{class:"st laal"},"laal")," neeche  ",el("span",{class:"st kam"},"kam data")," 300 se kam bet")));
 for(const [k,v] of Object.entries(d.strategies))m.append(el("div",{class:"card"},el("h2",{},fb(nm[k]||k)),el("table",{},el("thead",{},el("tr",{},["Samay","Bet","Hit","Hit %","95% range","Paper ROI","Haal"].map(x=>el("th",{},x)))),
  el("tbody",{},Object.entries(pn).map(([p,l])=>{const s=v[p];return el("tr",{},el("td",{},l),el("td",{},s.trials),el("td",{},s.hits),el("td",{},el("b",{},pct(s.hit_pct,2))),el("td",{class:"mut"},pct(s.ci_low,2)+" - "+pct(s.ci_high,2)),el("td",{class:s.roi95>=0?"ok":"bad"},(s.roi95>=0?"+":"")+pct(s.roi95,0)),el("td",{},el("span",{class:"st "+(s.status==="kam data"?"kam":s.status)},s.status)))})))));
 m.append(el("div",{class:"warn"},"95% range break-even (1.05%) ko chhoo rahi ho to asar pakka nahi hai. Kam bet par bharosa mat karo."))},

/* ---------------- 5. DATA ---------------- */
async data(m){
 const s=await api("GET","/status");ST=s;const out=el("pre",{},"");
 m.append(el("div",{class:"card"},el("h2",{},"Data aur Fetch"),el("p",{},"Aakhri line: ",el("b",{},s.last_date)," | kul din: ",el("b",{},s.days)," | agli khelne ki tarikh: ",el("b",{},s.play_date)),
  el("p",{class:"mut"},"Roz subah 7:00 baje GitHub Action apne aap naya result laata hai. Abhi chahiye to neeche button dabao (PIN lagega)."),
  el("div",{class:"row"},el("button",{class:"b",on:{click:async()=>{out.textContent="Site se la raha hai...";try{const r=await api("POST","/fetch",{stake:5});
    out.textContent=`Nayi lines: ${r.added.join(", ")||"koi nahi"}\nAakhri line: ${r.last_date} (kul ${r.days} din)\nPaper: ${r.settled} bet settle, ${r.new_bets} nayi\nDost badlaav: ${r.drift_changes}\n`+(r.errors.length?"Dikkat:\n"+r.errors.join("\n"):"")+(r.saved_to_github?"\nGitHub par save ho gaya":"")}catch(e){out.textContent=e.message}}}},"Abhi result fetch karo"),
   el("a",{href:"/api/download/results.csv"},el("button",{class:"b g"},"results.csv download"))),out));
 const l=s.last_fetch;m.append(el("div",{class:"card"},el("h2",{},"Pichla fetch"),l?el("pre",{},JSON.stringify(l,null,1)):el("p",{class:"mut"},"Abhi koi log nahi.")),
  el("div",{class:"card"},el("h2",{},"Backup"),el("p",{class:"mut"},"Phone me folder /sdcard/SahilLab_Data/ me results.csv ki copy rehti hai. Bhari ho jaye to purani files Google Drive me move kar do. Phone se fetch: Termux me  bash /sdcard/SahilLab_Data/fetch_now.sh")))}
});
