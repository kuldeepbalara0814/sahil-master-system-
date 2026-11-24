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

tabs.meri=async function(root){
 let w;try{w=await api("GET","/window")}catch(e){root.append(el("div",{class:"warn"},e.message));return}
 const nk=w.naksha_new||[],t30=w.top30||[],pl=w.plan||{},nm=w.pocket_names||{};
 const counted=!(pl.naksha&&pl.naksha.counted===false);
 root.append(el("div",{class:"hero"},
  el("div",{class:"eyebrow"},`Meri Window · ${dm(w.play_date)}`),
  el("h2",{},"Meri apni window"),
  el("div",{class:"big"},"Ye meri apni window hai: sirf mere chune hue. Baaki sab main app me chalta rehta hai."),
  el("div",{class:"mut small",style:"margin-top:8px"},w.scan_time?`Tokri lock hui: ${istm(w.scan_time)}`:"Tokri abhi lock nahi hui",` | pocket ki ginti ${dm(w.start)} se`),
  counted?null:el("div",{class:"small",style:"margin-top:6px"},`Aaj (${dm(w.play_date)}) ki tokri sirf dikhane ke liye; pocket ki ginti start tarikh (${dm(w.start)}) se.`)));
 /* naye Naksha pattern */
 root.append(el("div",{class:"card wn-naksha"},
  el("h2",{style:"margin:0 0 6px"},"Aaj ke naye Naksha pattern aur unki jodi"),
  nk.length?[el("div",{class:"row"},copyBtn("Sab jodi copy",nk.flatMap(p=>p.numbers),"sm")),
   ...nk.map(p=>el("div",{class:"wn-pat"},
    el("div",{class:"act-top"},el("b",{},p.title||p.name),copyBtn("Copy",p.numbers)),
    p.name&&p.title?el("p",{class:"mut small",style:"margin:2px 0"},p.name):null,
    el("p",{class:"mut small",style:"margin:2px 0"},"Game: "+(p.games||[]).map(fb).join(", ")),
    el("div",{class:"act-nums"},(p.numbers||[]).map(n=>chip(n,"green")))))]
  :el("p",{class:"mut"},"Aaj koi naya Naksha pattern nahi bana")));
 /* top 30 */
 root.append(el("div",{class:"card wn-top30"},
  el("h2",{style:"margin:0 0 6px"},"Top 30 jodi ",el("span",{class:"sub"},"(sab pattern me jo sabse zyada baar aayi)")),
  el("div",{class:"row"},copyBtn("Copy",t30.map(r=>r.n),"sm")),
  el("div",{class:"act-nums"},t30.map((r,i)=>el("span",{class:"chip "+(i<3?"green":i<6?"yellow":"grey"),title:`score ${r.score}, ${r.votes} pattern${r.baar?", aaj ke din (baar) ki tokri me":""}`},p2(r.n)))),
  el("p",{class:"mut small",style:"margin:6px 0 0"},"score = kitne alag pattern ne wo jodi di (+1 agar aaj ke din (baar) ki tokri me)")));
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
