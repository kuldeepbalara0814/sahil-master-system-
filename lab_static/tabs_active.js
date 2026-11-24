"use strict";
/* ACTIVE: auto-bane patterns me se jo abhi chal rahe hain / pichle 1-3 din me pass hue, ek jagah */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const dm=s=>{if(!s)return"";const [y,m,d]=String(s).slice(0,10).split("-").map(Number);return d?d+" "+MN[m-1]:s};
const tm=s=>String(s||"").replace("T"," ").slice(0,16);
const SRC={auto:"auto",manual:"manual"};

/* ---- HIT hue map + hath se result (prefix ht-) ---- */
const HG=["FB","GB","GL","DS"];
const SXH=()=>window.SCANX;
function htGet(k){try{return localStorage.getItem(k)}catch(e){return null}}
function htSet(k,v){try{localStorage.setItem(k,v)}catch(e){}}
function htMsg(r){
 if(r.already)return"Ye result pehle se ginti me hai (site wala hai, badla nahi ja sakta)";
 if(r.replaced)return"Hath wala result badal diya. "+(r.n_new>0?r.n_new+" map hit hue":"Koi map hit nahi hua");
 if(r.has_archive===false)return"Is din ke andaze saved nahi the";
 return r.n_new>0?r.n_new+" map hit hue":"Koi map hit nahi hua"}
function htHitLine(h){return el("p",{class:"ht-line"},el("b",{},"HIT: "),`${p2(h.n)} ${fb(h.game||"")} ${dm(h.date)}`,h.src==="manual"?el("span",{class:"mut small"}," (hath se)"):null)}
function howCard(r,dsT,fbT){
 // 009 ka Hinglish tarika + aaj ke ank ke 10 number (sirf samajhne ke liye)
 const a=dsT.find(x=>x.pos==="andar"),b=dsT.find(x=>x.pos==="bahar"),f=fbT;
 const ten=k=>[...Array(10).keys()].map(i=>k*10+i),one=k=>[...Array(10).keys()].map(i=>i*10+k);
 const rows=[["DS andar "+a.ank,ten(a.ank)],["DS bahar "+b.ank,one(b.ank)],["FB andar "+f.ank,ten(f.ank)]];
 const li=x=>el("li",{style:"margin:4px 0"},x);
 return el("div",{class:"card flat how009"},el("h2",{style:"margin:0 0 6px"},"009 kaise samjho (Hinglish)"),
  el("ul",{class:"small",style:"margin:0;padding-left:18px"},[
   "Andar = number ka pehla ank (dahai), bahar = doosra ank (ikai). Udaharan: 59 me andar 5, bahar 9.",
   "Niyam: 2 draw pehle wale number ka ank aaj usi game me usi jagah (andar/bahar) aaye to PASS.",
   "Sirf 3 line chuni gayi: DS andar, DS bahar, FB andar. GB, GL aur FB bahar chune nahi gaye, kyunki wo random ke paas the.",
   "Ye JODI ka khel nahi, ek ANK (0-9) ka hai. 'DS andar 5' = DS ke sirf 50-59; 'DS bahar 9' = sirf 09, 19, ..., 99; 'FB andar 1' = FB ke sirf 10-19. 36 ya 55 jodi ki tokri nahi: test me ~0 fayda mila.",
   "Rupaye: har ank Rs 30; jeet par 9.5 guna = Rs 285 (net +Rs 255); haar par -Rs 30. Roz 3 ank = Rs 90. Jeet ka chance ~12%, break-even 10.53%.",
   "Kagaz ka khata app apne aap rakhta hai."].map(li)),
  el("p",{class:"mut small",style:"margin:8px 0 4px"},"sirf samajhne ke liye: is ank ke 10 number"),
  rows.map(([l,ns])=>el("div",{style:"margin:4px 0"},el("span",{class:"small"},l+": "),el("span",{class:"act-nums",style:"display:inline-flex;flex-wrap:wrap;gap:4px"},ns.map(n=>el("span",{class:"chip grey",style:"font-size:12px;min-width:0;padding:1px 7px"},p2(n)))))))}
function ankPanels(heroBox,ankBox){
 // Sarvam mockup jaisa: hero + DS ank card + FB ank card (bada number, break-even wali bar, 3 tile, badge). Rang theme.css se.
 const rs=n=>"Rs "+Math.round(n).toLocaleString("en-IN"),sg=n=>(n>0?"+":n<0?"-":"")+rs(Math.abs(n));
 Promise.all([api("GET","/dsrule"),api("GET","/ank")]).then(([d,r])=>{
  const be=r.breakeven,f=r.forward,l=r.last90,line=(g,p)=>r.lines.find(x=>x.game===g&&x.pos===p),pos=r.balance>=r.capital;
  const t=g=>r.today.filter(x=>x.game===g),dsn=(d.modes.four.today.numbers||[]);
  const verdict=(rate)=>rate-be>=1?["up","break-even se upar (purana data)"]:rate>be?["mid","halka (break-even ke paas)"]:["low","break-even se neeche"];
  const tiles=(a,b2,c)=>el("div",{class:"mini3"},[a,b2,c].map(([k,v,s])=>el("div",{class:"t"},el("div",{class:"k"},k),el("div",{class:"v"},v),el("div",{class:"s"},s))));
  const best=r.lines.filter(x=>x.pick).sort((x,y)=>y.rate_2020-x.rate_2020)[0];
  heroBox.replaceChildren(el("div",{class:"hero"},
   el("div",{class:"eyebrow"},`Aaj ka saar · ${dm(r.play_date)}`),
   el("h2",{},"DS ke naye signal kagaz par chal rahe hain"),
   el("div",{class:"big"},`DS ke 4 number (008) + ${r.today.length} ank (009). Purane data par sabse upar: `,el("b",{},`${best.game} ${best.pos} ank (${best.rate_2020}%, 2020-26)`),". "),
   el("div",{class:"row2"},dsn.map(n=>el("span",{class:"chip blue"},p2(n))),r.today.map(x=>el("span",{class:"chip green",title:x.game+" "+x.pos},`${x.game} ${x.pos==="andar"?"a":"b"} ${x.ank}`))),
   el("div",{class:"quote"},"Ye sirf kagaz ka research hai: software dikhata hai, faisla aapka. Ye ank-level asar hai: DS ke dahai aur ikai ank alag-alag ~12% baar 2 draw pehle jaise aate hain; inka jod hi number ka lag-2 repeat (1.55%) hai. FB andar alag game ka hai. 90 din me kuch sabit nahi hota."),
   el("button",{type:"button",class:"b sm",style:"margin-top:10px",on:{click:()=>go("meri")}},"Meri Window kholo")));
  const sum=(ls,k)=>ls.reduce((a,x)=>a+x[k],0),pc=(h,n)=>n?(100*h/n).toFixed(1)+"%":"-";
  const sig=(title,ls,pairs,note)=>{const rate=Math.round(ls.reduce((a,x)=>a+x.rate_2020,0)/ls.length*100)/100,v=verdict(rate),
    all=Math.round(ls.reduce((a,x)=>a+x.rate,0)/ls.length*100)/100,h90=sum(ls,"hit90"),n90=sum(ls,"n90"),fh=sum(ls,"fw_hit"),fn=sum(ls,"fw_n");
   return el("div",{class:"card sig"},
   el("div",{class:"top"},el("div",{class:"eyebrow"},title),badge(v[0],v[1])),
   el("div",{class:"bigrow"},pairs.map(([n,lab,cls])=>el("div",{class:"bignum "+cls},String(n),el("small",{},lab)))),
   el("div",{class:"mut"},note),meter(rate,be,ls.map(x=>`${x.pos} ${x.rate_2020}%`).join(" · ")+" (2020-26)",`break-even ${be}%`),
   tiles(["13 saal (2013-26)",all+"%",ls.length>1?"in "+ls.length+" line ka ausat":"is line ka"],["Pichle 90 din",`${h90}/${n90}`,pc(h90,n90)+", kam data"],["Asli (24 Nov se)",`${fh}/${fn}`,fn?pc(fh,fn):"abhi shuru"]))};
  const dsA=line("DS","andar"),dsB=line("DS","bahar"),fbA=line("FB","andar"),dsT=t("DS"),fbT=t("FB")[0];
  ankBox.replaceChildren(
   sig("DS · ank (naya, 009)",[dsA,dsB],[[dsT.find(x=>x.pos==="andar").ank,"andar","mg"],[dsT.find(x=>x.pos==="bahar").ank,"bahar",""]],`2 draw pehle ${p2(dsT[0].src)} → andar ${dsT.find(x=>x.pos==="andar").ank}, bahar ${dsT.find(x=>x.pos==="bahar").ank} · ${r.payout}x`),
   sig("FB · ank (naya, 009)",[fbA],[[fbT.ank,"andar","mg"]],`2 draw pehle ${p2(fbT.src)} → andar ${fbT.ank} · ${r.payout}x`),
   el("div",{class:"card"},
    el("div",{class:"tiles",style:"margin-top:0"},el("div",{class:"tile"},el("div",{class:"k"},"Kagaz ki raqam (Rs "+r.stake+"/ank)"),el("div",{class:"v "+(pos?"ok":"bad")},rs(r.balance)),el("div",{class:"s"},`shuru ${rs(r.capital)}, 24 Nov se`))),
    el("details",{style:"margin-top:8px"},el("summary",{class:"mut small"},"8 line ki table (13 saal, 2013-2026)"),
     el("table",{class:"sheet",style:"width:100%;font-size:12px"},el("thead",{},el("tr",{},["Line","Hit %","2020-26","ROI 9.5x","z"].map(h=>el("th",{},h)))),
      el("tbody",{},r.lines.map(x=>el("tr",{},el("td",{},(x.pick?"✔ ":"")+x.game+" "+x.pos),el("td",{class:x.rate>be?"ok":"mut"},x.rate+"%"),el("td",{class:x.rate_2020>be?"ok":"mut"},x.rate_2020+"%"),el("td",{class:x.roi>=0?"ok":"bad"},(x.roi>=0?"+":"")+x.roi+"%"),el("td",{},String(x.z)))))),
     el("p",{class:"mut small",style:"margin:4px 0 0"},"✔ = chuni hui line (2013-19 me chuni, 2020-26 me parakhi). Random 10%.")),
    r.ledger.length?el("details",{style:"margin-top:8px"},el("summary",{class:"mut small"},"Roz ka khata (24 Nov se)"),
     el("table",{class:"sheet",style:"width:100%;font-size:12px"},el("thead",{},el("tr",{},["Din","Natija","Net","Raqam"].map(h=>el("th",{},h)))),
      el("tbody",{},r.ledger.map(x=>el("tr",{},el("td",{},dm(x.date)),el("td",{},x.bets.map(b=>`${b.game}${b.pos==="andar"?"a":"b"} ${b.want}${b.hit?"✔":"✘"+b.got}`).join("  ")),el("td",{class:x.net>=0?"ok":"bad"},sg(x.net)),el("td",{},rs(x.balance))))))):el("p",{class:"mut small",style:"margin:6px 0 0"},"Khata aaj ki line aate hi shuru hoga."),
    el("p",{class:"warn small",style:"margin:8px 0 0"},r.warning)),
   howCard(r,dsT,fbT))
 }).catch(e=>{ankBox.replaceChildren(el("div",{class:"warn"},e.message))})}
function dsRuleCard(box){
 let r=null,mode="one";
 try{mode=localStorage.getItem("ds_mode")||"one"}catch(e){}
 const rs=n=>"Rs "+Math.round(n).toLocaleString("en-IN"),sg=n=>(n>0?"+":n<0?"-":"")+rs(Math.abs(n));
 function draw(){
  const m=r.modes[mode],t=m.today,pos=m.net>=0;
  const seg=el("div",{class:"act-seg"},[["one","Roz 1 number"],["four","Roz 4 number"]].map(([k,l])=>el("button",{class:k===mode?"on":"",on:{click:()=>{mode=k;try{localStorage.setItem("ds_mode",k)}catch(e){}draw()}}},l)));
  box.replaceChildren(
   el("h2",{style:"margin:0 0 4px"},"DS rule ",el("span",{class:"sub"},"(kagaz ka khata, apne aap)")),
   el("p",{class:"mut small",style:"margin:0 0 8px"},`Shuru: ${dm(r.start)}. Har din bet apne aap lagta hai, jeet/haar apne aap judti hai. Rule frozen hai.`),seg,
   el("p",{style:"margin:10px 0 6px"},el("b",{},`Aaj (${dm(t.date)}) ka bet: `),`${t.numbers.map(p2).join(", ")} par Rs ${r.stake} har number (kul ${rs(t.bet)}). Jeet gaya to ${rs(t.win_if_hit)} milenge.`),
   el("div",{class:"act-nums"},t.numbers.map(n=>el("span",{class:"chip green"},p2(n)))),
   r.ref&&r.ref.rate!=null?meter(r.ref.rate,r.breakeven,`${r.ref.rate}% (${r.ref.since.slice(0,4)} se, purane data par)`,`break-even ${r.breakeven}% (95x)`):null,
   el("div",{class:"tiles",style:"margin-top:10px"},
    el("div",{class:"tile"},el("div",{class:"k"},"Abhi ki raqam"),el("div",{class:"v"},rs(m.balance)),el("div",{class:"s"},`shuru ${rs(r.capital)}`)),
    el("div",{class:"tile"},el("div",{class:"k"},"Kul munafa/ghata"),el("div",{class:"v "+(pos?"ok":"bad")},sg(m.net)),el("div",{class:"s"},`lagaya ${rs(m.bet)}, mila ${rs(m.win)}`)),
    el("div",{class:"tile"},el("div",{class:"k"},"Hit"),el("div",{class:"v"},`${m.hits} / ${m.stakes}`),el("div",{class:"s"},m.rate==null?"abhi koi din nahi":`${m.rate}% (random 1%, break-even ${r.breakeven}%)`)),
    el("div",{class:"tile"},el("div",{class:"k"},"Bina-hit streak"),el("div",{class:"v"},m.streak+" din"),el("div",{class:"s"},"sabse lambi "+m.longest)),
    el("div",{class:"tile"},el("div",{class:"k"},"Din"),el("div",{class:"v"},String(m.days)))),
   m.past_year?el("p",{class:"mut small",style:"margin:8px 0 0"},`Agar ye rule pichle ${m.past_year.days} din chalta (Rs ${r.stake}/number): ${m.past_year.hits} hit, ${sg(m.past_year.net)}; sabse neeche raqam ${rs(m.past_year.lowest)}, sabse lambi bina-hit streak ${m.past_year.longest} din.`):null,
   el("p",{class:"small",style:"margin:8px 0 0"},r.verdict),
   m.ledger.length?el("details",{style:"margin-top:8px",open:m.ledger.length<=10?"":null},el("summary",{class:"mut small"},"Roz ka khata"),
    el("table",{class:"sheet",style:"width:100%;font-size:12px"},el("thead",{},el("tr",{},["Din","Number","DS","Natija","Net","Raqam"].map(h=>el("th",{},h)))),
     el("tbody",{},m.ledger.map(x=>el("tr",{},el("td",{},dm(x.date)),el("td",{},x.numbers.map(p2).join(" ")),el("td",{},p2(x.ds)),el("td",{class:x.hit?"ok":"mut"},x.hit?"HIT":"miss"),el("td",{class:x.net>=0?"ok":"bad"},sg(x.net)),el("td",{},rs(x.balance))))))):el("p",{class:"mut small",style:"margin:8px 0 0"},"Khata "+dm(r.start)+" ke baad ke pehle result se shuru hoga."),
   el("h3",{style:"margin:12px 0 4px"},"Niyam"),
   el("ol",{class:"small",style:"margin:0;padding-left:18px"},r.rules.map(x=>el("li",{style:"margin:3px 0"},x))),
   el("div",{class:"warn",style:"margin-top:8px"},r.warning))}
 box.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load..."));
 api("GET","/dsrule").then(x=>{r=x;draw()}).catch(e=>box.replaceChildren(el("div",{class:"warn"},e.message)))}
function htOpen(it){
 const box=el("div",{class:"ht-view"}),b=el("button",{type:"button",class:"b g sm"},"Kholo (rang me dekho)");let on=false;
 b.addEventListener("click",async()=>{on=!on;
  if(!on){box.replaceChildren();b.textContent="Kholo (rang me dekho)";return}
  b.textContent="Band karo";box.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load..."));
  try{const fam=String(it.id).startsWith("family:");
   const v=await api("GET",(fam?"/scanner/month_view?id=":"/scanner/view?id=")+encodeURIComponent(it.id));
   const sx=window.SCANX;if(!sx||!sx.chart)throw new Error("Pattern Scan tab ek baar kholo, phir yahan dobara");
   box.replaceChildren(fam&&sx.famMonth?sx.famMonth(v):sx.chart(v))}
  catch(e){box.replaceChildren(el("div",{class:"warn"},"Ye map ab dobara nahi ban pa raha: "+e.message))}});
 return {btn:b,box}}
function htCard(it){
 const sx=SXH(),op=htOpen(it);
 return el("div",{class:"ht-card"+(sx&&sx.reviewed(it.id)?" seen":"")},
  el("b",{},it.title||it.name),
  it.title&&it.name&&it.title!==it.name?el("p",{class:"mut small",style:"margin:2px 0"},it.name):null,
  (it.recent||[]).map(htHitLine),
  el("div",{class:"row",style:"margin-top:6px"},
   sx?sx.seenUI(it.id,()=>{}):null,sx?sx.editUI(it.id):null,
   op.btn,el("button",{type:"button",class:"b g sm",on:{click:()=>go("scan")}},"Pura dekho")),op.box)}
function htGroup(g){return el("div",{},el("div",{class:"act-grp"},`${g.naam} (${g.count})`),(g.items||[]).map(htCard))}
function htDraw(box,rep,days,redraw){
 const groups=rep.groups||[],show=htGet("ht_n2")==="1";
 const n2=groups.find(g=>g.key==="naksha2"),main=groups.filter(g=>g.key!=="naksha2"&&g.count>0);
 const tog=n2?el("div",{class:"ht-n2"},el("button",{type:"button",class:"b g sm",on:{click:()=>{htSet("ht_n2",show?"0":"1");redraw()}}},show?"Naksha 2 (Rashi) chhupao":"Naksha 2 (Rashi) bhi dikhao"),
  el("span",{class:"mut small"}," zyada map, kam matlab"+(show?"":` (${n2.count} hit)`))):null;
 const shown=[...main,...(show&&n2&&n2.count>0?[n2]:[])];
 const tot=main.reduce((a,g)=>a+g.count,0)+(show&&n2?n2.count:0);
 box.replaceChildren(...[
  el("h2",{class:"act-h"},`Hit hue map (pichle ${days} din)`,el("span",{class:"ht-tot"},String(tot))),el("p",{class:"mut small",style:"margin:-4px 0 8px"},"Hit = kisi map ke andaze wala number kisi bhi game me aaya. (Neeche 'PASS' alag cheez hai: pattern poora hua.)"),
  rep.mismatch&&rep.mismatch.length?el("div",{class:"warn",style:"margin-bottom:8px"},el("b",{},"Dhyan do: "),rep.mismatch.map(m=>el("p",{class:"small",style:"margin:3px 0"},typeof m==="string"?m:JSON.stringify(m)))):null,
  shown.length?shown.map(htGroup):el("p",{class:"mut"},"Abhi koi map hit nahi hua."),tog].flat().filter(Boolean))}
async function htLoadHits(box,days){
 box.replaceChildren(el("p",{class:"load"},el("span",{class:"spin"}),"Hit map dekh raha hoon..."));
 try{const rep=await api("GET","/hits?days="+days);const redraw=()=>htDraw(box,rep,days,redraw);redraw()}
 catch(e){box.replaceChildren(el("div",{class:"warn"},e.message))}}

function htManual(box,onSaved){
 let st=null,game=null;
 function known(g){const x=st&&st.games&&st.games[g];return x?`${g} ${p2(x.n)} (${x.src==="manual"?"hath se":"site"})`:g}
 function draw(){
  const inp=el("input",{type:"text",inputmode:"numeric",maxlength:"2",placeholder:"00",class:"ht-in","aria-label":"Result number"});
  inp.addEventListener("input",()=>{inp.value=inp.value.replace(/\D/g,"").slice(0,2)});
  inp.addEventListener("blur",()=>{if(inp.value.length===1)inp.value=p2(inp.value)});
  const save=el("button",{type:"button",class:"b big2 ht-save",on:{click:async()=>{
   const v=inp.value.trim();if(!/^\d{1,2}$/.test(v)){toast("Number 00 se 99 ke beech dalo");return}
   save.disabled=true;
   try{const r=await api("POST","/result/manual",{game,number:+v,date:st.date});toast(htMsg(r));await onSaved()}
   catch(e){toast(e.message)}finally{save.disabled=false}}}},"Save");
  box.replaceChildren(el("h2",{style:"margin:0 0 4px"},"Result dalo ",el("span",{class:"sub"},"(hath se)")),
   el("p",{class:"mut small",style:"margin:0 0 8px"},"Khel ki tareekh: ",el("b",{},dm(st.date))),
   el("div",{class:"ht-chips"},HG.map(g=>el("button",{type:"button",class:"ht-chip"+(g===game?" on":""),on:{click:()=>{game=g;draw()}}},known(g)))),
   el("div",{class:"row ht-form"},inp,save),
   ...HG.filter(g=>st.games&&st.games[g]&&st.games[g].src==="manual").map(g=>el("div",{class:"row",style:"margin-top:8px"},
    el("span",{class:"small"},`${g} ${p2(st.games[g].n)} (hath se dala). Galat ho to `),
    el("button",{type:"button",class:"b g sm",on:{click:()=>{game=g;draw();const i=box.querySelector("input");if(i)i.focus()}}},"Badlo"),
    el("button",{type:"button",class:"b g sm",on:{click:async()=>{if(!confirm(`${g} ka hath wala result hatana hai?`))return;
     try{await api("POST","/result/manual/delete",{game:g,date:st.date});toast("Hath wala result hata diya");await onSaved()}catch(e){toast(e.message)}}}},"Hatao"))),
   el("p",{class:"mut small",style:"margin:8px 0 0"},"Site se result aate hi ye apne aap ginta hai; jaldi dekhna ho to yaha hath se dalo."))}
 return async function init(){
  try{st=await api("GET","/result/manual");
   if(!game||!HG.includes(game))game=HG.find(g=>!(st.games&&st.games[g]))||"FB";draw()}
  catch(e){box.replaceChildren(el("div",{class:"warn"},e.message))}}}
tabs.active=async function(root){
 let days=3,rep=null,busy=false;
 try{days=+localStorage.getItem("act_days")||3}catch(e){}
 const strip=el("div",{class:"card act-strip"}),body=el("div"),hitBox=el("div",{class:"ht-sec"}),manBox=el("div",{class:"card ht-man"});
 const manInit=htManual(manBox,async()=>{await manInit();await load(false);if(hitBox.scrollIntoView)hitBox.scrollIntoView({behavior:"smooth",block:"start"})});
 const skel=()=>body.replaceChildren(el("div",{class:"act-skel"}),el("div",{class:"act-skel"}),el("div",{class:"act-skel"}));
 async function load(post){
  skel();busy=true;htLoadHits(hitBox,days);
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
   s?el("div",{class:"row"},el("span",{class:"pill "+(s.auto_today>=3?"g":"o")},`Aaj auto scan: ${s.auto_today} (din me 3: subah 7, shaam 7, raat 12:30 IST; 9 baje wala sirf dobara koshish)`),el("span",{class:"pill m"},`Manual: ${s.manual_today}`)):null,
   el("div",{class:"row"},btn,seg)].filter(Boolean));}
 function nums(t){return t&&t.numbers&&t.numbers.length?el("div",{class:"act-nums"},t.numbers.map(n=>el("span",{class:"chip green"},p2(n)))):null}
 const SX=()=>window.SCANX;
 function links(it){const sx=SX(),op=htOpen(it);return el("div",{},el("div",{class:"row"},
  sx?sx.seenUI(it.id,()=>draw()):null,sx?sx.editUI(it.id):null,op.btn,
  el("button",{class:"b g sm",on:{click:()=>go("scan")}},"Pura dekho"),
  el("a",{href:"/api/scanner/xlsx?id="+encodeURIComponent(it.id)},el("button",{class:"b g sm"},"Excel"))),op.box)}
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
   el("h2",{class:"act-h"},`Pichle ${n} din me PASS hue`),el("p",{class:"mut small",style:"margin:-4px 0 8px"},"PASS = pattern poora hua (uski shart puri). Upar 'Hit hue map' alag hai: usme sirf number aana ginta hai, isliye dono ginti alag aa sakti hain."),
   pass.length?grouped(pass,true):el("p",{class:"mut"},`Pichle ${n} din me koi pass nahi hua.`),
   rep.recent_fail?el("p",{class:"mut small"},`Pichle ${n} din me ${rep.recent_fail} FAIL bhi hue.`):null,
   el("h2",{class:"act-h"},"Scoreboard (pichle 30 din)"),el("div",{class:"card flat"},board())].flat().filter(Boolean))}
 const dsBox=el("div",{class:"card"});dsRuleCard(dsBox);const heroBox=el("div"),ankBox=el("div");ankPanels(heroBox,ankBox);
 root.append(heroBox,el("button",{type:"button",class:"card rk-link",on:{click:()=>go("rank")}},"Aaj ke number ranking dekho"),manBox,dsBox,ankBox,el("div",{class:"card"},el("h2",{style:"margin:0 0 4px"},"Active ",el("span",{class:"sub"},"(jo pattern abhi chal rahe hain)")),
  el("p",{class:"mut small",style:"margin:0"},"Ek baar bana pattern kabhi gayab nahi hota. Scan din me 3 baar apne aap hota hai (subah 7, shaam 7, raat 12:30 IST).")),strip,hitBox,body);
 drawStrip();manInit();await load(false);
};
})();
