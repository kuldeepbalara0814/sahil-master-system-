"use strict";
/* MERI WINDOW: sirf mere chune hue - aaj ke naye Naksha pattern ki jodi + Top 30 jodi, ladder FB10/GB15/GL20/DS25, 2 pocket (kagaz) */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const dm=s=>{if(!s)return"";const [y,m,d]=String(s).slice(0,10).split("-").map(Number);return d?d+" "+MN[m-1]:s};
const rs=n=>"Rs "+Math.round(n).toLocaleString("en-IN"),sg=n=>(n>0?"+":n<0?"-":"")+rs(Math.abs(n));
function copyText(txt){
 const fallback=()=>{const ta=el("textarea",{style:"position:fixed;left:-9999px;top:0;opacity:0",readonly:true});ta.value=txt;document.body.append(ta);ta.focus();ta.select();
  let ok=false;try{ok=document.execCommand("copy")}catch(e){}ta.remove();return ok};
 try{if(navigator.clipboard&&navigator.clipboard.writeText&&window.isSecureContext!==false)
  return navigator.clipboard.writeText(txt).then(()=>true,()=>fallback())}catch(e){}
 return Promise.resolve(fallback())}
async function doCopy(nums){
 const txt=[...new Set(nums)].sort((a,b)=>a-b).map(p2).join(" ");
 if(!txt){toast("Copy karne ko number nahi hai");return}
 const ok=await copyText(txt);toast(ok?"Copy ho gaya: "+txt:"Copy nahi hua, dobara try karo")}
const copyBtn=(label,nums,cls)=>el("button",{type:"button",class:"b "+(cls||"g sm"),on:{click:()=>doCopy(nums)}},label);

/* SVG line graph: balance curve + capital ki seedhi dashed line */
function graph(curve,capital){
 if(!curve||!curve.length)return el("p",{class:"mut small wn-empty"},"abhi koi poora din nahi");
 const NS="http://www.w3.org/2000/svg",W=320,H=130,L=8,R=8,T=10,B=18;
 const pts=[{date:"",balance:capital},...curve];
 const vs=pts.map(p=>p.balance),lo=Math.min(...vs,capital),hi=Math.max(...vs,capital),span=(hi-lo)||1;
 const X=i=>L+(pts.length>1?i*(W-L-R)/(pts.length-1):0),Y=v=>T+(hi-v)*(H-T-B)/span;
 const mk=(t,a)=>{const e=document.createElementNS(NS,t);for(const[k,v]of Object.entries(a))e.setAttribute(k,v);return e};
 const svg=mk("svg",{viewBox:`0 0 ${W} ${H}`,class:"wn-graph",role:"img","aria-label":"Balance ka graph"});
 svg.append(mk("line",{x1:L,x2:W-R,y1:Y(capital),y2:Y(capital),class:"wn-base","stroke-dasharray":"4 4"}));
 svg.append(mk("polyline",{points:pts.map((p,i)=>`${X(i).toFixed(1)},${Y(p.balance).toFixed(1)}`).join(" "),class:"wn-line",fill:"none"}));
 pts.forEach((p,i)=>{if(i)svg.append(mk("circle",{cx:X(i).toFixed(1),cy:Y(p.balance).toFixed(1),r:2.5,class:"wn-dot"}))});
 const t1=mk("text",{x:L,y:H-4,class:"wn-ax"});t1.textContent=dm(curve[0].date);
 const t2=mk("text",{x:W-R,y:H-4,class:"wn-ax","text-anchor":"end"});t2.textContent=dm(curve[curve.length-1].date);
 const t3=mk("text",{x:W-R,y:Y(capital)-3,class:"wn-ax","text-anchor":"end"});t3.textContent=rs(capital);
 svg.append(t1,t2,t3);return svg}

function natija(d){
 const st=(d.steps||[]).filter(s=>!s.hit).map(s=>s.game+" haar");
 if(d.status==="hit"){return [...st,`${d.hit.game} HIT ${p2(d.hit.n)} (${sg(d.net)})`].join(", ")}
 if(d.status==="no_hit")return "koi hit nahi";
 if(d.status==="pending")return (st.length?st.join(", ")+", ":"")+"baaki"+(d.next?` (agla: ${d.next.game} Rs ${d.next.stake})`:"");
 if(d.status==="low")return "raqam kam, ladder ruki";
 return "aaj koi jodi nahi"}
function planLine(p,pk){
 if(!p||!p.count)return "Aaj ke liye koi jodi nahi.";
 return `Aaj ke liye: ${p.count} jodi. `+p.ladder.map((s,i)=>`${i?"na aaye to ":""}${s.game} par Rs ${s.stake} x ${p.count} = ${rs(s.cost)}`).join("; ")+`. Sabse zyada kharcha ${rs(p.worst_cost)}.`}

function pocketCard(key,pk,plan,names,tdy){
 const t=pk.totals,bg=t.by_game||{},pos=pk.net>=0;
 const tile=(k,v,s,c)=>el("div",{class:"tile"},el("div",{class:"k"},k),el("div",{class:"v "+(c||"")},v),el("div",{class:"s"},s||""));
 const days=pk.days||[];
 return el("div",{class:"card wn-pocket","data-pocket":key},
  el("h2",{style:"margin:0 0 4px"},names[key]||key," ",el("span",{class:"sub"},`(kagaz, shuru ${rs(pk.capital)})`)),
  plan&&plan.counted===false?el("p",{class:"mut small",style:"margin:0 0 6px"},`Aaj (${dm(tdy)}) ki tokri sirf dikhane ke liye hai; pocket ki ginti start tarikh se.`):null,
  el("div",{class:"tiles"},
   tile("Ab ka paisa",rs(pk.balance),`shuru ${rs(pk.capital)}`,pos?"ok":"bad"),
   tile("Net",sg(pk.net),`kharcha ${rs(t.spent||0)}`,pos?"ok":"bad"),
   tile("ROI",(pk.roi>0?"+":"")+(+pk.roi).toFixed(1)+"%","kharche par"),
   tile("Din",String(t.days||0),`no-hit ${t.no_hit||0}`),
   tile("Hit wale din",String(t.hit_days||0),t.days?Math.round(100*(t.hit_days||0)/t.days)+"% din":"-"),
   tile("Sabse badi giraawat",rs(pk.max_drawdown||0),"unchi se neeche")),
  graph(pk.curve,pk.capital),
  el("p",{class:"small",style:"margin:8px 0 4px"},el("b",{},"Kis game me hit hua: "),["FB","GB","GL","DS"].map(g=>`${g} ${bg[g]||0}`).join(" | ")),
  days.length?el("details",{style:"margin-top:6px",open:days.length<=8?"":null},el("summary",{class:"mut small"},"Roz ka hisaab"),
   el("table",{class:"sheet",style:"width:100%;font-size:12px"},el("thead",{},el("tr",{},["Din","Jodi","Natija","Net","Raqam"].map(h=>el("th",{},h)))),
    el("tbody",{},days.map(d=>el("tr",{},el("td",{},dm(d.date)),el("td",{},String(d.count)),el("td",{class:d.status==="hit"?"ok":"mut"},natija(d)),
     el("td",{class:d.net>=0?"ok":"bad"},d.status==="pending"&&!d.net?"-":sg(d.net)),el("td",{},rs(d.balance))))))):el("p",{class:"mut small",style:"margin:6px 0 0"},"Roz ka hisaab pehle poore din ke baad shuru hoga."),
  el("p",{class:"small wn-plan",style:"margin:8px 0 0"},planLine(plan,key)))}

/* ---- pattern number se kholo (Pattern Scan / Number Rank wale 'Pattern 03' number ke hisaab se) ---- */
const KINDS=[["naksha","Naksha"],["naksha2","Naksha-Rashi"],["steps","Puzzle-Steps"],["family","Family"],["copy","Copy"],["dana","Dana-Farak"]];
const NAAM2KEY={"Naksha-Rashi":"naksha2","Puzzle-Steps":"steps","Family":"family","Jodi-Copy":"copy","Dana-Farak":"dana"};
const STX={aaj:["o","aaj ka andaza"],pass:["g","PASS"],fail:["r","FAIL"],dekho:["m","dekho"]};
let REP=null,DETAIL=null,OPENCARD=null;
const itemsOf=k=>{const p=REP&&REP.patterns.find(x=>x.key===k);return p?p.items:[]};
const labelOf=(k,i)=>"Pattern "+p2(i+1)+(k==="naksha"?"":" ("+(KINDS.find(x=>x[0]===k)||[0,k])[1]+")");
/* 'Pattern 04 (Puzzle-Steps)' jaisa label -> (kind, number) */
function parseLabel(s){const m=/^Pattern\s+(\d+)(?:\s*\((.+)\))?\s*$/.exec(String(s).trim());if(!m)return null;
 const naam=m[2]?m[2].trim():"Naksha",key=naam==="Naksha"?"naksha":(NAAM2KEY[naam]||(KINDS.find(x=>x[1]===naam)||[])[0]);return key?{key,no:+m[1]}:null}
async function openItem(k,no){
 const list=itemsOf(k),it=list[no-1];
 if(!DETAIL)return;
 if(!it){DETAIL.replaceChildren(el("div",{class:"warn"},`${(KINDS.find(x=>x[0]===k)||[0,k])[1]} me Pattern ${p2(no)} nahi hai (1 se ${list.length} tak hain).`));return}
 const sx=window.SCANX;if(!sx||!sx.chart){DETAIL.replaceChildren(el("div",{class:"warn"},"Chart abhi load nahi hua, page dobara kholo"));return}
 const body=el("div",{},el("p",{class:"mut"},el("span",{class:"spin"}),"Load..."));
 const st=STX[it.status]||STX.dekho,tg=(it.targets||[]);
 DETAIL.replaceChildren(el("div",{class:"card flat wn-detail"},
  el("div",{class:"act-top"},el("h3",{style:"margin:0"},`${labelOf(k,no-1)} · ${it.name||""}`),el("span",{},el("span",{class:"pill "+st[0]},st[1]),it.new?el("span",{class:"pill g",style:"margin-left:6px"},"NAYA"):null)),
  el("div",{class:"b"},it.title||""),(it.lines||[]).map(l=>el("p",{class:"mut small",style:"margin:3px 0"},l)),
  tg.length?el("div",{},el("div",{class:"small"},el("b",{},"Aaj ke andaze (jodi): ")),tg.map(t=>el("div",{class:"row",style:"gap:6px;margin:4px 0"},el("span",{class:"small"},fb(t.game)+":"),(t.numbers||[]).map(n=>chip(n,"green","sm")),copyBtn("Copy",t.numbers||[],"g sm")))):null,
  el("div",{class:"row",style:"margin:8px 0"},el("a",{href:"/api/scanner/xlsx?id="+encodeURIComponent(it.id)},el("button",{type:"button",class:"b sm"},"Excel me dekho (download)")),
   el("button",{type:"button",class:"b g sm",on:{click:()=>DETAIL.replaceChildren()}},"Band karo")),body));
 try{const v=it.kind==="family"?sx.famMonth(await api("GET","/scanner/month_view?id="+encodeURIComponent(it.id))):sx.chart(await api("GET","/scanner/view?id="+encodeURIComponent(it.id)));body.replaceChildren(v)}
 catch(e){body.replaceChildren(el("div",{class:"warn"},e.message))}
 if(OPENCARD&&OPENCARD.scrollIntoView)OPENCARD.scrollIntoView({behavior:"smooth",block:"start"})}
function openCard(w){
 let kind="naksha",flt="aaj";
 const box=el("div"),num=el("input",{type:"text",inputmode:"numeric",placeholder:"number likho (jaise 03)",style:"width:170px","aria-label":"Pattern number"});
 DETAIL=el("div");
 const goNum=()=>{const n=parseInt(String(num.value).replace(/\D/g,""),10);if(!n){toast("Pattern ka number likho");return}openItem(kind,n)};
 num.addEventListener("keydown",e=>{if(e.key==="Enter")goNum()});
 const draw=()=>{
  const all=itemsOf(kind),shown=all.map((it,i)=>[it,i+1]).filter(([it])=>flt==="all"||(flt==="aaj"?it.status==="aaj":it.new));
  const cnt=k=>{const a=itemsOf(k);return a.filter(x=>x.status==="aaj").length+"/"+a.length};
  box.replaceChildren(
   el("div",{class:"row",style:"gap:6px;margin:8px 0"},KINDS.map(([k,l])=>el("button",{type:"button",class:"b sm"+(k===kind?"":" g"),on:{click:()=>{kind=k;draw()}}},`${l} ${cnt(k)}`))),
   el("div",{class:"row",style:"gap:6px;margin:6px 0"},[["aaj","Aaj ke andaze wale"],["new","Sirf naye (aaj bane)"],["all","Sab"]].map(([k,l])=>el("button",{type:"button",class:"b sm"+(k===flt?"":" g"),on:{click:()=>{flt=k;draw()}}},l))),
   el("div",{class:"row",style:"margin:8px 0"},num,el("button",{type:"button",class:"b",on:{click:goNum}},"Kholo")),
   ...(shown.length?shown.map(([it,no])=>{const st=STX[it.status]||STX.dekho,tg=it.targets||[];
    return el("div",{class:"wn-pat"},el("div",{class:"act-top"},el("b",{},`No. ${p2(no)} · ${it.name||""}`),el("span",{},el("span",{class:"pill "+st[0]},st[1]),it.new?el("span",{class:"pill g",style:"margin-left:6px"},"NAYA"):null)),
     el("p",{class:"mut small",style:"margin:2px 0"},it.title||""),
     tg.length?el("div",{class:"act-nums"},[...new Set(tg.flatMap(t=>t.numbers||[]))].sort((a,b)=>a-b).map(n=>chip(n,"green","sm"))):null,
     el("div",{class:"row",style:"gap:6px"},el("button",{type:"button",class:"b sm",on:{click:()=>openItem(kind,no)}},"Kholo"),
      el("a",{href:"/api/scanner/xlsx?id="+encodeURIComponent(it.id)},el("button",{type:"button",class:"b g sm"},"Excel"))))})
   :[el("p",{class:"mut"},"Is filter me abhi koi pattern nahi. 'Sab' dabao ya number seedha likho.")]))};
 draw();
 OPENCARD=el("div",{class:"card wn-open"},
  el("h2",{style:"margin:0 0 4px"},"Pattern number se kholo ",el("span",{class:"sub"},`(aaj ${dm(w.play_date)} ke pattern)`)),
  el("p",{class:"mut small",style:"margin:0"},"Number wahi hai jo Pattern Scan aur Number Rank me 'Pattern 03' likha dikhta hai. Pehle kind chuno (Naksha, Family...), phir number likho, ya list se 'Kholo' dabao. Rang wala chart khulega aur Excel me bhi dekh sakte ho."),
  el("p",{class:"mut small",style:"margin:4px 0 0"},"Pattern tab tak is list me rehta hai jab tak uska aakhri result nahi aa jata; uske baad apne aap hat jata hai (list roz naye scan se banti hai, purane chalte hue 'purane' bhi isi me hain)."),
  box,DETAIL);
 return OPENCARD}

tabs.meri=async function(root){
 let w;try{w=await api("GET","/window")}catch(e){root.append(el("div",{class:"warn"},e.message));return}
 try{REP=await api("GET","/scanner")}catch(e){REP=null}
 const nk=w.naksha_new||[],t30=w.top30||[],pl=w.plan||{},nm=w.pocket_names||{};
 const counted=!(pl.naksha&&pl.naksha.counted===false);
 root.append(el("div",{class:"hero"},
  zimg("zolly_body.webp","zl-hero",84),
  el("div",{class:"eyebrow"},`Meri Window · ${dm(w.play_date)}`),
  el("h2",{},"Meri apni window"),
  el("div",{class:"big"},"Ye meri apni window hai: sirf mere chune hue. Baaki sab main app me chalta rehta hai."),
  el("div",{class:"mut small",style:"margin-top:8px"},w.scan_time?`Tokri lock hui: ${istm(w.scan_time)}`:"Tokri abhi lock nahi hui",` | pocket ki ginti ${dm(w.start)} se`),
  counted?null:el("div",{class:"small",style:"margin-top:6px"},`Aaj (${dm(w.play_date)}) ki tokri sirf dikhane ke liye; pocket ki ginti start tarikh (${dm(w.start)}) se.`)));
 if(REP)root.append(openCard(w));
 /* NAKSHA KE NUMBER: aaj aur kal - pehle bane naksha ke aage wale '?' box samet */
 const GM=["FB","GB","GL","DS"],ydBox=el("div",{class:"wn-yaadbox"},el("p",{class:"load"},el("span",{class:"spin"}),"Naksha ke number gine ja rahe hain..."));
 const ydCard=(v,kal)=>{
  if(!v||!(v.items||[]).length)return null;
  const hits=v.items.filter(e=>e.hit);
  return el("div",{class:"card wn-yaad"},
   el("h2",{style:"margin:0 0 6px"},kal?`Kal ka natija: Naksha (${dm(v.date)})`:`Naksha ke sab number: ${dm(v.date)}`," ",el("span",{class:"sub"},"(naye + pehle bane)")),
   kal?el("p",{class:"small",style:"margin:2px 0"},hits.length?`${hits.length} naksha box me asli number aaya (hara).`:"Kisi naksha box me asli number nahi aaya."):el("div",{class:"row"},copyBtn("Sab naksha number copy",v.all,"sm")),
   GM.filter(g=>(v.games[g]||[]).length).map(g=>{const r=(v.result||{})[g];
    return el("div",{class:"wn-pat"},
     el("div",{class:"act-top"},el("b",{},fb(g)+(r!==undefined?` : aaya ${p2(r)}`:"")),copyBtn("Copy",v.games[g])),
     el("div",{class:"act-nums"},v.games[g].map(n=>chip(n,n===r?"green":"grey","sm"))),
     el("details",kal&&hits.some(e=>e.game===g)?{open:"open"}:{},el("summary",{class:"mut small"},"Kaun se naksha me kya ban raha hai"),
      v.items.filter(e=>e.game===g).map(e=>el("div",{class:"small",style:"margin:4px 0"},
       el("b",{},e.name)," ",e.numbers.map(n=>chip(n,e.hit&&n===r?"green":"blue","sm")),
       el("span",{class:"mut"},` ${e.title}${e.pehle>1?` | ${e.pehle} din pehle se dikh raha`:""}`)))))}),
   el("p",{class:"mut small",style:"margin:6px 0 0"},"Naksha chart ke aage wale '?' box, pichle 8 din ke scan se (sirf Naksha 1). 900 din ki jaanch me inka hit random jitna hi nikla; faisla aapka."))};
 root.append(ydBox);
 api("GET","/yaad").then(yd=>{const cs=[ydCard(yd.aaj,false),ydCard(yd.kal,true)].filter(Boolean);ydBox.replaceChildren(...cs)}).catch(e=>ydBox.replaceChildren(el("div",{class:"warn"},"Naksha ke number nahi aaye: "+e.message)));
 /* naye Naksha pattern */
 root.append(el("div",{class:"card wn-naksha"},
  el("h2",{style:"margin:0 0 6px"},"Aaj ke naye Naksha pattern aur unki jodi"),
  nk.length?[el("div",{class:"row"},copyBtn("Sab jodi copy",nk.flatMap(p=>p.numbers),"sm")),
   ...nk.map(p=>el("div",{class:"wn-pat"},
    el("div",{class:"act-top"},el("b",{},p.title||p.name),el("span",{class:"row",style:"gap:6px"},copyBtn("Copy",p.numbers),(()=>{const no=itemsOf("naksha").findIndex(x=>x.id===p.id)+1;return no?el("button",{type:"button",class:"b sm",on:{click:()=>openItem("naksha",no)}},"Kholo (No. "+p2(no)+")"):null})())),
    p.name&&p.title?el("p",{class:"mut small",style:"margin:2px 0"},p.name):null,
    el("p",{class:"mut small",style:"margin:2px 0"},"Game: "+(p.games||[]).map(fb).join(", ")),
    el("div",{class:"act-nums"},(p.numbers||[]).map(n=>chip(n,"green")))))]
  :el("p",{class:"mut"},"Aaj koi naya Naksha pattern nahi bana")));
 /* top 30 */
 root.append(el("div",{class:"card wn-top30"},
  el("h2",{style:"margin:0 0 6px"},"Top 30 jodi ",el("span",{class:"sub"},"(sab pattern me jo sabse zyada baar aayi)")),
  el("div",{class:"row"},copyBtn("Copy",t30.map(r=>r.n),"sm")),
  el("div",{class:"act-nums"},t30.map((r,i)=>el("span",{class:"chip "+(i<3?"green":i<6?"yellow":"grey"),title:`score ${r.score}, ${r.votes} pattern${r.baar?", aaj ke din (baar) ki tokri me":""}`},p2(r.n)))),
  el("p",{class:"mut small",style:"margin:6px 0 0"},"score = kitne alag pattern ne wo jodi di + dost ke point (har dost-list me aane par 1) + baar ki tokri me ho to 2"),
  REP&&t30.some(r=>(r.maps||[]).length)?el("details",{style:"margin-top:8px"},el("summary",{class:"mut small"},"Kaun se pattern se aayi (label par dabao to wo pattern khulega)"),
   t30.map(r=>el("div",{class:"wn-pat"},el("div",{class:"row",style:"gap:6px"},chip(r.n,"blue","sm"),(r.maps||[]).map(lb=>{const pl2=parseLabel(lb);
    return pl2?el("button",{type:"button",class:"b g sm",on:{click:()=>openItem(pl2.key,pl2.no)}},lb):el("span",{class:"pill m"},lb)}))))):null));
 /* aaj ke SAB Naksha number (purane + naye) - sirf dikhane ke liye */
 const na=w.naksha_all||[];
 if(na.length)root.append(el("div",{class:"card wn-nkall"},
  el("h2",{style:"margin:0 0 6px"},"Aaj ke sab Naksha + Steps number ",el("span",{class:"sub"},"(purane + naye)")),
  el("div",{class:"row"},copyBtn("Sab copy",na.map(r=>r.n),"sm")),
  el("div",{class:"act-nums"},na.map(r=>el("span",{class:"chip "+(r.top30?"green":r.votes>=2?"yellow":"grey"),title:`${r.naksha?"Naksha "+r.naksha:""}${r.naksha&&r.steps?", ":""}${r.steps?"Steps "+r.steps:""}${r.baar?", baar":""}${r.dost?", dost x"+r.dost:""}${r.top30?", Top 30 me":""}`},p2(r.n)))),
  el("p",{class:"mut small",style:"margin:6px 0 0"},`${na.length} number. Hara = Top 30 me bhi hai; peela = 2+ vote; baaki halka. Naksha 1 ke saare aaj-wale (purane+naye) aur Puzzle-Steps ke number. Naksha-Rashi isme nahi. Sirf dikhane ke liye, paper basket nahi.`)));
 /* aaj ke Dost + Baar number - sirf dikhane ke liye */
 const db=w.dost_baar||[];
 if(db.length)root.append(el("div",{class:"card wn-dostbaar"},
  el("h2",{style:"margin:0 0 6px"},"Aaj ke Dost + Baar number ",el("span",{class:"sub"},"(sirf dikhane ke liye)")),
  el("div",{class:"row"},copyBtn("Sab copy",db.map(r=>r.n),"sm"),copyBtn("Top 30 copy",db.slice(0,30).map(r=>r.n),"sm")),
  el("div",{class:"act-nums"},db.map((r,i)=>el("span",{class:"chip "+(r.top30?"green":i<12?"yellow":"grey"),title:`score ${r.score}: dost ${r.dost}${r.baar?", baar (+2)":""}${r.top30?", Top 30 me":""}`},p2(r.n)))),
  el("p",{class:"mut small",style:"margin:6px 0 0"},`${db.length} number. Dost = pichhli line ke har number ke 12 dost (5 hara, 4 peela, 3 narangi), teeno samay; list me jitni baar utne point. Baar ki tokri ke number ko 2 point. Hara = Top 30 me bhi. Backtest (13 saal): ye tokri random se behtar nahi nikli (28.6% vs 30%), isliye Top 30 isse nahi bani; yahan sirf dekhne ke liye.`)));
 /* 2 pocket */
 for(const k of ["naksha","top30"])if(w.pockets&&w.pockets[k])root.append(pocketCard(k,w.pockets[k],pl[k],nm,w.play_date));
 /* tarika */
 root.append(el("div",{class:"card flat wn-how"},el("h2",{style:"margin:0 0 6px"},"Tarika (Hinglish me samjho)"),
  el("ul",{class:"small",style:"margin:0;padding-left:18px"},[
   "Kya hai: do chhoti tokri (Naksha ki naye pattern wali jodi, aur Top 30 jodi). Har tokri ka alag kagaz ka pocket, har ek Rs 10,000.",
   "Ladder: pehle FB par har jodi Rs 10; na aaye to GB par Rs 15; na aaye to GL par Rs 20; na aaye to DS par Rs 25. Jis game me hit aaya, us din wahin ruk jao.",
   "Udaharan: 20 jodi hon to FB par Rs 200, GB par Rs 300, GL par Rs 400, DS par Rs 500. Hit par har jodi ka 95 guna (40 ya zyada jodi par 90 guna).",
   `Tokri roz ke pehle scan me lock ho jati hai, baad me nahi badalti. Pocket ki ginti ${dm(w.start)} se.`,
   "Ye sirf kagaz ka research hai. Software dikhata hai, faisla aapka."].map(x=>el("li",{style:"margin:4px 0"},x)))));
};
})();
