"use strict";
/* RECORD (range + Excel) aur GUIDE */
(function(){
const MN=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const iso=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
const parse=s=>{const [y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d)};
const monthsBack=(d,n)=>{const x=new Date(d.getFullYear(),d.getMonth()-n,d.getDate()+1);return x};
const MAXM=12;                                             // preview me max itne mahine

function sheet(rows){
 const by=new Map(rows.map(r=>[r[0],r.slice(1)]));
 const ym=[...new Set(rows.map(r=>r[0].slice(0,7)))].sort();
 const shown=ym.slice(-MAXM),years=[...new Set(shown.map(k=>k.slice(0,4)))];
 const out=el("div");
 for(const y of years){
  const ms=shown.filter(k=>k.startsWith(y)).map(k=>+k.slice(5));
  const t=el("table",{class:"sheet"}),th=el("thead");
  th.append(el("tr",{},el("th",{class:"ttl",colspan:1+4*ms.length},`YEAR ${y} — ANNUAL RESULT CHART (FB | GB | GL | DS)`)));
  th.append(el("tr",{},el("th",{class:"d",rowspan:2},"Date"),ms.map(mm=>el("th",{class:"mh",colspan:4},`${MN[mm-1]}-${y.slice(2)}`))));
  th.append(el("tr",{},ms.flatMap(()=>["FB","GB","GL","DS"].map(g=>el("th",{class:"sh"},g)))));
  const tb=el("tbody");
  for(let d=1;d<=31;d++){
   tb.append(el("tr",{},el("td",{class:"d"},d),ms.flatMap(mm=>{const v=by.get(`${y}-${String(mm).padStart(2,"0")}-${String(d).padStart(2,"0")}`);return [0,1,2,3].map(j=>el("td",{},v?p2(v[j]):""))})));
  }
  t.append(th,tb);out.append(el("div",{class:"sheetwrap",style:"margin-bottom:12px"},t));
 }
 return {node:out,cut:ym.length>shown.length};
}

tabs.record=async function(m){
 const last=parse(ST.last_date);
 const from=el("input",{type:"date",min:"2013-01-01",max:ST.last_date}),to=el("input",{type:"date",min:"2013-01-01",max:ST.last_date});
 const info=el("p",{class:"mut"}),prev=el("div"),dl=el("a",{href:"#"},el("button",{class:"b"},"Excel download"));
 const presets=[["Is mahina",()=>new Date(last.getFullYear(),last.getMonth(),1)],["Pichle 3 mahine",()=>monthsBack(last,3)],["Pichle 6 mahine",()=>monthsBack(last,6)],
  ["Pichle 12 mahine",()=>monthsBack(last,12)],["Is saal",()=>new Date(last.getFullYear(),0,1)],["Poora (2013 se)",()=>new Date(2013,0,1)]];
 const preset=f=>{from.value=iso(f());to.value=iso(last);show()};
 async function show(){
  if(!from.value||!to.value)return;
  if(from.value>to.value)return toast("'Se' tarikh 'Tak' se badi hai");
  const q=`from=${from.value}&to=${to.value}`;dl.href=`/api/export/record.xlsx?${q}`;
  prev.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load ho raha hai..."));
  try{const d=await api("GET","/record?"+q);
   info.textContent=d.count?`${d.count} din ka result (${d.rows[0][0]} se ${d.rows[d.rows.length-1][0]} tak)`:"Is range me koi din nahi.";
   if(!d.count){prev.replaceChildren();return}
   const s=sheet(d.rows);prev.replaceChildren(s.node,s.cut?el("p",{class:"note small"},`Yahan sirf aakhri ${MAXM} mahine dikh rahe hain. Poora range Excel me aayega.`):null)}
  catch(e){prev.replaceChildren(el("div",{class:"warn"},e.message))}}
 from.onchange=to.onchange=show;
 m.append(el("div",{class:"card"},el("h2",{},"Record ",el("span",{class:"sub"},"(Excel jaisa chart)")),
  el("p",{class:"mut"},"Kab se kab tak ka chahiye chuno, ya neeche se jaldi wala button dabao. Neeche chart dikhega aur 'Excel download' se wahi chart aap ke Excel me aa jayega (saath me seedhi table wali sheet bhi, filter ke liye)."),
  el("div",{class:"presets"},presets.map(([n,f])=>el("button",{class:"b g sm",on:{click:()=>preset(f)}},n))),
  el("div",{class:"row"},el("span",{},"Se:"),from,el("span",{},"Tak:"),to,dl),info),
  el("div",{class:"card flat",style:"padding:10px"},prev),
  el("p",{class:"mut small"},"DS us line me likha agli subah ka Desawar hai. Mahine ka aakhri din chhuti hai, isliye khaali dikhega."));
 preset(presets[1][1]);
};

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
