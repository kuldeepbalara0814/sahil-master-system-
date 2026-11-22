"use strict";
/* DIN (BAAR): saatho weekday ki tokri (6 seedha number + palat), kab-kab aaya, kaun sa din sabse mazboot */
(function(){
const WN={0:"Somvar (Monday)",1:"Mangalvar (Tuesday)",2:"Budhvar (Wednesday)",3:"Guruvar (Thursday)",4:"Shukravar (Friday)",5:"Shanivar (Saturday)",6:"Ravivar (Sunday)"};
tabs.baar=async function(m){
 let days=365,rep=null;
 const box=el("div"),rank=el("div"),info=el("p",{class:"mut small"});
 const dsel=el("select",{on:{change:()=>{days=+dsel.value;load()}}},[[365,"Pichla 1 saal"],[1095,"Pichle 3 saal"],[1825,"Pichle 5 saal"],[0,"Poora record (13 saal)"]].map(([v,t])=>el("option",{value:v},t)));
 async function load(){
  box.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load ho raha hai..."));
  try{rep=await api("GET","/baar/all?days="+days);draw()}catch(e){box.replaceChildren(el("div",{class:"warn"},e.message))}}
 function dayCard(it){
  const today=it.weekday===rep.today_weekday,det=el("div");let on=false;
  const seedha=it.top.map(t=>el("span",{class:"chip orange",title:`${t.count} baar aaya`},p2(t.n)+" · "+t.count));
  const palat=it.top.map(t=>el("span",{class:"chip "+(t.palat===t.n?"grey":"blue"),title:t.palat===t.n?"palat khud wahi":"palat"},p2(t.palat)+(t.palat===t.n?"*":"")));
  const btn=el("button",{class:"b g sm"},"Kab-kab aaya (tarikh aur game)");
  btn.onclick=()=>{on=!on;btn.textContent=on?"Band karo":"Kab-kab aaya (tarikh aur game)";
   det.replaceChildren(...(on?[el("div",{class:"tw"},el("table",{},el("thead",{},el("tr",{},["Number","Baar","Kab (tarikh, game)"].map(h=>el("th",{},h)))),
    el("tbody",{},it.top.map(t=>el("tr",{},el("td",{class:"b"},p2(t.n)),el("td",{},t.count),el("td",{class:"small"},t.when.join(", ")))))))]:[]))};
  return el("div",{class:"card"+(today?" tgtcard":"")},
   el("div",{class:"row",style:"justify-content:space-between"},el("h2",{style:"margin:0"},WN[it.weekday]+(today?" - aaj":"")),el("span",{class:"pill m"},`${it.rank}vi jagah | ${it.strength} baar`)),
   el("p",{class:"mut small"},`${it.cases} din (${it.from} se ${it.to}). 6 sabse zyada aaye number (seedha) aur unke palat.`),
   el("p",{class:"b",style:"margin:6px 0 2px"},"Seedha (zyada se kam):"),el("div",{class:"row",style:"gap:6px"},seedha),
   el("div",{class:"palbox"},el("div",{class:"palh"},"PALAT (ye palat hai)"),el("div",{class:"row",style:"gap:6px"},palat),el("div",{class:"mut small"},`Kul number: ${it.numbers.length}  (* = palat khud wahi)`)),
   it.ties.length?el("p",{class:"mut small"},`Barabari wale aur (${it.top[it.top.length-1].count} baar): ${it.ties.slice(0,14).map(p2).join(" ")}`):null,
   btn,det)}
 function draw(){
  info.textContent=`Data: ${rep.items[0].from} se ${rep.items[0].to} tak. Aaj khelne ki tarikh: ${rep.play_date}.`;
  rank.replaceChildren(el("p",{class:"b"},"Kaun sa din sabse zyada (6 number ke baar ka jod):"),el("div",{class:"row",style:"gap:6px"},rep.order.map((w,i)=>{const it=rep.items.find(x=>x.weekday===w);return el("span",{class:"pill "+(i===0?"g":"m")},`${i+1}. ${WN[w].split(" ")[0]} (${it.strength})`)})));
  box.replaceChildren(...rep.items.map(dayCard))}
 m.append(el("div",{class:"card"},el("h2",{},"Din (Baar) ",el("span",{class:"sub"},"(har weekday ke sabse zyada aaye number)")),
  el("p",{class:"mut"},"Har din (Ravivar se Shanivar) ke liye us din jo 6 number sabse zyada aaye wo 'seedha' hain, unke palat neeche box me. 'Kab-kab aaya' dabao to har number ki tarikh aur game dikhegi. Ye sirf hint hai, jaanch me ye random se behtar nahi nikla. Aaj ki List ke 'Baar Filter' me apni jodi daal kar bhi dekh sakte ho."),
  el("div",{class:"row"},el("span",{},"Data:"),dsel),info,rank),box);
 await load();
};
})();
