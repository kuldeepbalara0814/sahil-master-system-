"use strict";
/* RECORD (range + Excel) aur GUIDE */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const iso=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
const parse=s=>{const [y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d)};
const monthsBack=(d,n)=>{const x=new Date(d.getFullYear(),d.getMonth()-n,d.getDate()+1);return x};
const MAXM=12;                                             // preview me max itne mahine

function sheet(rows,marks){
 const by=new Map(rows.map(r=>[r[0],r.slice(1)]));
 const mk=new Map();for(const m of marks||[]){const k=m.date+"|"+m.g;(mk.get(k)||mk.set(k,[]).get(k)).push(m)}
 const ym=[...new Set(rows.map(r=>r[0].slice(0,7)))].sort();
 const shown=ym.slice(-MAXM),years=[...new Set(shown.map(k=>k.slice(0,4)))];
 const out=el("div");
 for(const y of years){
  const ms=shown.filter(k=>k.startsWith(y)).map(k=>+k.slice(5));
  const t=el("table",{class:"sheet"}),th=el("thead");
  th.append(el("tr",{},el("th",{class:"ttl",colspan:1+4*ms.length},`YEAR ${y} — ANNUAL RESULT CHART (FB | GB | GL | DS)`)));
  th.append(el("tr",{},el("th",{class:"d",rowspan:2},"Date"),ms.map(mm=>el("th",{class:"mh mb mr",colspan:4},`${MN[mm-1]}-${y.slice(2)}`))));
  th.append(el("tr",{},ms.flatMap(()=>["FB","GB","GL","DS"].map((g,j)=>el("th",{class:"sh"+(j==0?" mb":"")+(j==3?" mr":"")},g)))));
  const tb=el("tbody");
  for(let d=1;d<=31;d++){
   tb.append(el("tr",{},el("td",{class:"d"},d),ms.flatMap(mm=>{const key=`${y}-${String(mm).padStart(2,"0")}-${String(d).padStart(2,"0")}`,v=by.get(key);
    return [0,1,2,3].map(j=>{const ms2=mk.get(key+"|"+j),m=ms2&&ms2[ms2.length-1];
     const td=el("td",{class:(j==0?"mb ":"")+(j==3?"mr ":"")+(m?"mk "+m.kind:"")},m&&m.kind==="due"?m.text:(v?p2(v[j]):""));
     if(m){td.style.background="#"+m.color;td.style.color="#000";td.title=ms2.map(x=>x.tip).join("\n");if(m.kind==="pass")td.style.outline="3px solid #fff";if(m.kind==="due")td.style.fontSize="11px"}
     return td})})));
  }
  t.append(th,tb);out.append(el("div",{class:"sheetwrap",style:"margin-bottom:12px"},t));
 }
 return {node:out,cut:ym.length>shown.length};
}

const GAPS=[1,2,3,4,5,6,7,8,9,10],QDAYS=[12,15,20,30,45,60,90];
const dm=s=>{const d=parse(s);return `${d.getDate()} ${MN[d.getMonth()]}`};
const pr=c=>c[0]===c[1]?p2(c[0]):`${p2(c[0])}/${p2(c[1])}`;

tabs.record=async function(m){
 const last=parse(ST.last_date);
 // ---- gap filter ----
 const gset=new Set([3,4,5,6,7]);let gdays=15,gshow="all",gres=null;
 const gbox=el("div",{class:"row"}),gnote=el("p",{class:"mut small"}),gtab=el("div");
 const gdays_in=el("input",{type:"number",min:3,max:400,value:gdays,style:"width:80px"});
 const gq=()=>`gaps=${[...gset].sort((a,b)=>a-b).join(",")}&days=${gdays}&show=${gshow}`;
 async function gload(){
  if(!gset.size){gtab.replaceChildren(el("p",{class:"mut"},"Kam se kam ek gap chuno."));gres=null;return show()}
  gtab.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Dhundh raha hai..."));
  try{gres=await api("GET","/gaps?"+gq());
   const c=gres.chains;
   gnote.textContent=`${dm(gres.start)} se ${dm(gres.end)} tak (${gres.days} din) me ${c.length} chain mili.`;
   gtab.replaceChildren(c.length?el("div",{class:"tw"},el("table",{class:"t gt"},
    el("thead",{},el("tr",{},["","Number/palat","Gap","Step bane","3rd step","Haal"].map(h=>el("th",{},h)))),
    el("tbody",{},c.map(ch=>el("tr",{},
     el("td",{},el("span",{class:"dot",style:"background:#"+ch.color})),
     el("td",{class:"b"},pr(ch.cls)),el("td",{},`${ch.gap} din`),
     el("td",{class:"small"},ch.steps.map(st=>`${dm(st.date)} ${st.hits.map(h=>h.game+" "+p2(h.n)).join("/")}`).join(" → ")),
     el("td",{},ch.due?dm(ch.due):(ch.next_due?"agla "+dm(ch.next_due):(ch.len>=3?dm(ch.steps[2].date):"-"))),
     el("td",{},el("span",{class:"pill "+({aane:"o",pass:"g",miss:"r",chhuti:"m"}[ch.status])},ch.status_text))))))):el("p",{class:"mut"},"Is range me koi chain nahi bani."));
  }catch(e){gtab.replaceChildren(el("div",{class:"warn"},e.message));gres=null}
  show();dl.href=`/api/export/record.xlsx?from=${from.value}&to=${to.value}&${gq()}`}
 const gcard=el("div",{class:"card"},el("h2",{},"Gap Filter ",el("span",{class:"sub"},"(ek jaise gap se bane step)")),
  el("p",{class:"mut"},"Ek number (ya uska palat) kisi bhi game me aaye aur wahi ek jitne din ke gap par dobara aaye to 2 step bane. 3rd step ab us tarikh par aane wala hai. Chart me narangi (ya alag rang) se mark hoga, 3rd step ki tarikh par 'NN?' likha aayega. Aa gaya to 'pass', nahi aaya to 'nahi aaya'."),
  el("div",{class:"row"},el("span",{},"Gap (din):"),GAPS.map(g=>{const cb=el("input",{type:"checkbox",checked:gset.has(g),on:{change:()=>{cb.checked?gset.add(g):gset.delete(g);gload()}}});return el("label",{class:"chk"},cb,String(g))})),
  el("div",{class:"row"},el("span",{},"Pichle kitne din me step bane:"),gdays_in,QDAYS.map(n=>el("button",{class:"b g sm",on:{click:()=>{gdays=n;gdays_in.value=n;gload()}}},`${n}`))),
  el("div",{class:"row"},el("span",{},"Dikhao:"),el("select",{on:{change:e=>{gshow=e.target.value;gload()}}},[["all","Sab"],["aane","Sirf aane wale"],["pass","Sirf pass"],["miss","Sirf nahi aaya"]].map(([v,t])=>el("option",{value:v},t)))),
  gnote,gtab);
 gdays_in.onchange=()=>{gdays=Math.max(3,Math.min(400,+gdays_in.value||15));gdays_in.value=gdays;gload()};
 const from=el("input",{type:"date",min:"2013-01-01",max:ST.last_date}),to=el("input",{type:"date",min:"2013-01-01",max:ST.last_date});
 const info=el("p",{class:"mut"}),prev=el("div"),dl=el("a",{href:"#"},el("button",{class:"b"},"Excel download"));
 const presets=[["Is mahina",()=>new Date(last.getFullYear(),last.getMonth(),1)],["Pichle 3 mahine",()=>monthsBack(last,3)],["Pichle 6 mahine",()=>monthsBack(last,6)],
  ["Pichle 12 mahine",()=>monthsBack(last,12)],["Is saal",()=>new Date(last.getFullYear(),0,1)],["Poora (2013 se)",()=>new Date(2013,0,1)]];
 const preset=f=>{from.value=iso(f());to.value=iso(last);show()};
 async function show(){
  if(!from.value||!to.value)return;
  if(from.value>to.value)return toast("'Se' tarikh 'Tak' se badi hai");
  const q=`from=${from.value}&to=${to.value}`;dl.href=`/api/export/record.xlsx?${q}`+(gres?"&"+gq():"");
  prev.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load ho raha hai..."));
  try{const d=await api("GET","/record?"+q);
   info.textContent=d.count?`${d.count} din ka result (${d.rows[0][0]} se ${d.rows[d.rows.length-1][0]} tak)`:"Is range me koi din nahi.";
   if(!d.count){prev.replaceChildren();return}
   const s=sheet(d.rows,gres&&gres.marks);prev.replaceChildren(...[s.node,s.cut?el("p",{class:"note small"},`Yahan sirf aakhri ${MAXM} mahine dikh rahe hain. Poora range Excel me aayega.`):null].filter(Boolean));const mk0=prev.querySelector("td.mk");if(mk0){const w=mk0.closest(".sheetwrap");setTimeout(()=>{w.scrollLeft=Math.max(0,mk0.offsetLeft-80);w.scrollTop=Math.max(0,mk0.offsetTop-90)},50)}}
  catch(e){prev.replaceChildren(el("div",{class:"warn"},e.message))}}
 from.onchange=to.onchange=show;
 m.append(gcard,el("div",{class:"card"},el("h2",{},"Record ",el("span",{class:"sub"},"(Excel jaisa chart)")),
  el("p",{class:"mut"},"Kab se kab tak ka chahiye chuno, ya neeche se jaldi wala button dabao. Neeche chart dikhega aur 'Excel download' se wahi chart aap ke Excel me aa jayega (saath me seedhi table wali sheet bhi, filter ke liye)."),
  el("div",{class:"presets"},presets.map(([n,f])=>el("button",{class:"b g sm",on:{click:()=>preset(f)}},n))),
  el("div",{class:"row"},el("span",{},"Se:"),from,el("span",{},"Tak:"),to,dl),info),
  el("div",{class:"card flat",style:"padding:10px"},prev),
  el("p",{class:"mut small"},"DS us line me likha agli subah ka Desawar hai. Mahine ka aakhri din chhuti hai, isliye khaali dikhega."));
 m.append(grCard());
 preset(presets[1][1]);gload();
};

// ---- Har game ka alag record (FB/GB/GL/DS) ----
function grCard(){
 const GAMES=[["FB","FB","2013 se"],["GB","GB","2013 se"],["GL","GL","2013 se"],["DS","DS","1966 se"]];
 let g="FB",basis="line",year=null,years=[],seq=0;
 try{const x=localStorage.getItem("gr_game");if(GAMES.some(a=>a[0]===x))g=x}catch(e){}
 const seg=el("div",{class:"gr-seg"}),ysel=el("select",{class:"gr-year"}),body=el("div"),info=el("p",{class:"mut small gr-info"}),
  bbox=el("div",{class:"gr-basis"}),xl=el("a",{class:"gr-dl",href:"#"},el("button",{class:"b"},"Excel download")),cs=el("a",{class:"gr-dl",href:"#"},el("button",{class:"b g"},"CSV download"));
 const pv=el("button",{class:"b g sm",on:{click:()=>step(1)}},"< Pichla"),nx=el("button",{class:"b g sm",on:{click:()=>step(-1)}},"Agla >");
 function step(d){const i=years.indexOf(year);const j=i+d;if(i<0||j<0||j>=years.length)return;year=years[j];load()}
 function links(){const q=`g=${g}&basis=${basis}`;xl.href="/api/record/game.xlsx?"+q;cs.href="/api/record/game.csv?"+q}
 function drawSeg(){seg.replaceChildren(...GAMES.map(([k,n,s])=>el("button",{class:g===k?"on":"",on:{click:()=>{if(g===k)return;g=k;year=null;try{localStorage.setItem("gr_game",g)}catch(e){}drawSeg();drawBasis();load()}}},n," ",el("small",{},s))))}
 function drawBasis(){
  bbox.replaceChildren();if(g!=="DS")return;
  bbox.append(el("div",{class:"mut small"},"Tarikh:"),el("div",{class:"gr-seg"},
   el("button",{class:basis==="line"?"on":"",on:{click:()=>{basis="line";year=null;drawBasis();load()}}},"hamare record jaisi (line)"),
   el("button",{class:basis==="khula"?"on":"",on:{click:()=>{basis="khula";year=null;drawBasis();load()}}},"khulne ki tarikh (site jaisi)")),
   el("p",{class:"mut small"},"Line: DS ka number us tarikh ki line me jo agli subah khulta hai. Khulne ki tarikh: number usi din par jis din site par khula."))}
 ysel.onchange=()=>{year=+ysel.value;load()};
 async function load(){
  const my=++seq;links();
  body.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load ho raha hai..."));
  try{
   const d=await api("GET",`/record/game?g=${g}&basis=${basis}`+(year?`&year=${year}`:""));
   if(my!==seq)return;
   years=d.years.slice().reverse();year=d.year;
   ysel.replaceChildren(...years.map(y=>el("option",{value:y,selected:y===year},String(y))));ysel.value=String(year);
   const i=years.indexOf(year);pv.disabled=i>=years.length-1;nx.disabled=i<=0;
   const t=el("table",{class:"gr-t"}),hr=el("tr",{},el("th",{class:"d"},"Din"),d.months.map(x=>el("th",{},x)));
   t.append(el("thead",{},hr));
   t.append(el("tbody",{},d.grid.map((r,k)=>el("tr",{},el("td",{class:"d"},String(k+1)),r.map(v=>v===null||v===undefined?el("td",{class:"e"},"-"):el("td",{},p2(v)))))));
   body.replaceChildren(el("div",{class:"gr-wrap"},t));
   info.textContent=`Record: ${d.first} se ${d.last} | ${d.count} din`+(d.note?" | "+d.note:"");
  }catch(e){if(my!==seq)return;body.replaceChildren(el("div",{class:"warn"},e.message));info.textContent=""}}
 drawSeg();drawBasis();links();
 const c=el("div",{class:"card gr-card"},el("h2",{},"Har game ka alag record ",el("span",{class:"sub"},"(FB, GB, GL, DS)")),
  el("p",{class:"mut"},"Chuno kaun sa game aur kaun sa saal. Chart purane chart jaisa hai: upar mahine, side me din 1-31."),
  seg,bbox,el("div",{class:"row gr-yr"},pv,ysel,nx),body,info,
  el("div",{class:"row gr-btns"},xl,cs),
  el("p",{class:"mut small"},"Ye sheet sab-ek-me record se bante hain, isliye naya result aate hi apne aap update ho jaati hain."));
 load();return c}

tabs.guide=async function(m){
 const sec=(t,items)=>el("div",{class:"card"},el("h2",{},t),el("ul",{class:"g"},items.map(x=>el("li",{},x))));
 m.append(sec("Ye software kya karta hai",[
  "DATA: 2013 se aaj tak ka FB GB GL DS record (4,900+ din, koi duplicate nahi). Roz subah site se nayi line apne aap judti hai, ya 'Data' tab me button se.",
  "DOST KHOJO: koi bhi number likho (jaise 30). Uske sabse zyada saath aane wale 10 number 3 samay ke hisaab se dikhte hain: poora 13 saal, pichle 3 mahine, is mahina. Hara = top 3, peela = beech ke 3, narangi = last 4. Dost list ko kuch karna nahi padta, data aate hi ye apne aap badal jati hai.",
  "AAJ KI LIST: roz ka single jodi (kal ka GB number, FB+GL+DS par) aur har game ki 10 number ki list. Aaj ke result daalo to baad ke game ki list badal jaati hai.",
  "LAB: apna idea apni bhasha me likho, computer 13 saal ke result par test karta hai (neeche dekho).",
  "PAPER TRADING: kalpnik paisa se bet lagti hai, result aate hi jeet/haar apne aap, aur Monitor batata hai ki asar chal raha hai ya ghat gaya.",
  "RECORD: kab se kab tak ka chahiye chuno, chart dekho aur Excel download karo (aap ki sheet jaisa)."]));
 m.append(sec("Lab kaise use karein",[
  "Idea apni bhasha me likho, jaise: 'kal GB me jo aaya wahi aaj FB me lagao', 'kal GB ka palat aaj GL me', 'FB me 30 ke top 5 dost lagao', 'pichle 30 din me sabse zyada aaye wo 10 number GB me'.",
  "'Samjho' dabao. Computer likhega 'maine ye samjha'. Galat ho to 'Galat samjha?' kholkar dropdown se theek karo.",
  "'Backtest karo' dabao. Har din ke liye dekha jata hai ki us din tak ke data se idea kya lagata, aur number aaya ya nahi. Aage ka data kabhi nahi dekha jata.",
  "Natija: hara = kuch dum, peela = thoda asar par pakka nahi, laal = random jaisa. Hit % ko break-even 1.05% aur random 1.00% se milao.",
  "Sabse zaroori: 'Pehle ka hissa' aur 'Baad ka hissa' alag dekho. Purane saal me chala idea aaj nahi chalta to bharosa mat karo.",
  "Mumkin cheezein: kal/parso/N din pehle ka kisi bhi game ka number, wahi/palat/+1/-1/family/dost, number fix (30 aaye to...), hot/cold number, din (Somvar...) ka filter."]));
 m.append(sec("Roz ka routine",[
  "Subah 7 baje: GitHub Action kal ki poori line lata hai (DS subah 5:30 ko khulta hai). Paper bet settle hoti hai aur aaj ki nayi bet lagti hai.",
  "Aap: 'Aaj ki List' dekho, chaho to apni paper bet lagao. Shaam ko FB/GB/GL ke result upar likhkar agle game ki list dekho.",
  "Mahine me ek baar 'Monitor' dekho: hit % break-even (1.05%) se upar hai ya nahi."]));
 m.append(sec("Padhne ka tareeka",[
  "'Hit %' = 100 me kitni baar number aaya. Random = 1.00%. Break-even = 1.05% (95 guna par). Isse upar = paper par fayda.",
  "'Kam data' ka nishaan = us samay me number bahut kam baar aaya, isliye wahan ka dost pakka nahi.",
  "'x5.8' = us samay me ye dost overall se 5.8 guna zyada aaya. Chhote data me ye bada dikh sakta hai.",
  "Drift = dost badalna, jaise 10 par pehle 93 tha ab 94. Ye roz apne aap pakda jaata hai (Dost Khojo tab ke neeche)."]));
 m.append(sec("Sachchai (zaroor padho)",[
  "Result lagbhag random hain. Hamare 13 saal ke test me sirf chhota asar mila: number kuch din ke andar dobara aate hain. Ye asar 2013-2018 me bada tha, 2022-25 me lagbhag gayab, 2026 me thoda wapas.",
  "Mahine me 1-3 hit aate hain, aur kai mahine ek bhi nahi. Paper par chhota fayda dikh sakta hai par utaar-chadhaav bahut hai.",
  "Ye sirf paper trading aur software banane/seekhne ke liye hai. Asli paisa lagane ki salaah nahi."]));
 m.append(sec("Files / hosting",[
  "data/results.csv = poora record. data/paper_ledger.json = paper bet. data/ideas.json = save kiye idea. monitor.json, drift_log.json = monitor aur badlaav.",
  "Roz 7:00 IST: .github/workflows/daily.yml. Phone se: scripts/fetch_now.sh. Web: Render (render.yaml); env me GITHUB_TOKEN aur ADMIN_PIN.",
  "Code: lab/ (data, friends, picks, paper, monitor, fetcher, update, backtest, idea, export_xlsx), lab_server.py (web), lab_static/ (ye page), tests/."]))
};
})();
