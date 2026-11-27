"use strict";
/* AUTO PAPER POCKETS: Monitor tab ke upar. Har list ka apna Rs 10,000 ka kagaz ka pocket (/api/pockets). */
(function(){
const rs=n=>(n<0?"-":"")+"Rs "+Math.abs(Math.round(n)).toLocaleString("en-IN");
const d2=s=>{const [,m,d]=String(s).split("-").map(Number);return d+" "+["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][m-1]};
const WORD={hit:"HIT",no_hit:"nahi aaya",pending:"baaki",nothing:"tokri khali",low:"paisa kam"};
function table(head,rows){return el("div",{style:"overflow-x:auto"},el("table",{},el("thead",{},el("tr",{},head.map(h=>el("th",{},h)))),el("tbody",{},rows)))}
function detail(p){
 return el("div",{class:"card flat pk-detail"},
  el("h3",{style:"margin:0 0 6px"},p.naam),
  el("p",{class:"small",style:"margin:0 0 6px"},`Balance ${rs(p.balance)} | hit ${p.totals.hit_days}/${p.totals.days} din (random me ummeed ${p.totals.expected_hit_days}) | FB ${p.totals.by_game.FB}, GB ${p.totals.by_game.GB}, GL ${p.totals.by_game.GL}, DS ${p.totals.by_game.DS}`),
  el("div",{class:"small"},el("b",{},`Aaj ki tokri (${p.today.length}): `),p.today.map(n=>String(n).padStart(2,"0")).join(" ")||"-"),
  p.months.length?table(["Mahina","Opening","Fayda/Nuksan","Closing"],p.months.map(m=>el("tr",{},el("td",{},m.month),el("td",{},rs(m.opening)),el("td",{class:m.net>=0?"ok":"bad"},rs(m.net)),el("td",{},rs(m.closing))))):null,
  p.lines.length?table(["Tarikh","Jodi","Haal","Kahan","Kharcha","Fayda/Nuksan","Balance"],p.lines.map(x=>el("tr",{},el("td",{},d2(x.date)),el("td",{},x.count),el("td",{class:x.status==="hit"?"ok":x.status==="no_hit"?"bad":"mut"},WORD[x.status]||x.status),
    el("td",{},x.hit?`${fb(x.stop)} ${String(x.hit.n).padStart(2,"0")}`:"-"),el("td",{},rs(x.spent)),el("td",{class:x.net>0?"ok":x.net<0?"bad":""},rs(x.net)),el("td",{},rs(x.balance))))):el("p",{class:"mut small"},"Abhi koi din gina nahi gaya."))}
async function card(){
 const box=el("div",{class:"card pk-index"},el("h2",{style:"margin:0 0 6px"},"Auto paper pockets (sirf kagaz)"),el("p",{class:"load"},el("span",{class:"spin"}),"Load..."));
 api("GET","/pockets").then(j=>{
  const more=el("div");
  box.replaceChildren(el("h2",{style:"margin:0 0 6px"},"Auto paper pockets (sirf kagaz)"),
   el("p",{class:"small",style:"margin:0 0 6px"},`Har list ka apna ${rs(j.capital)}. Ginti ${d2(j.start)} se. Har jodi par FB 10, GB 15, GL 20, DS 25; hit par us din ruk. Mahine ka closing agle mahine ka opening.`),
   el("div",{class:"row",style:"margin-bottom:6px"},el("a",{href:"/api/pockets.xlsx",download:""},el("button",{type:"button",class:"b sm"},"Excel statement download"))),
   table(["Pocket","Balance","Fayda/Nuksan","Hit din","Random ummeed","Aaj jodi",""],j.pockets.map(p=>{const net=p.balance-p.capital;return el("tr",{},el("td",{},p.naam),el("td",{},rs(p.balance)),el("td",{class:net>0?"ok":net<0?"bad":"mut"},rs(net)),
     el("td",{},`${p.totals.hit_days}/${p.totals.days}`),el("td",{class:"mut"},p.totals.expected_hit_days),el("td",{},p.today.length),
     el("td",{},el("button",{type:"button",class:"b g sm",on:{click:()=>{more.replaceChildren(detail(p));if(more.scrollIntoView)more.scrollIntoView({behavior:"smooth"})}}},"Kholo")))})),
   more,
   el("p",{class:"mut small",style:"margin:6px 0 0"},"Hit din ko 'Random ummeed' se milao: usse zyada na ho to koi fayda saabit nahi. Hisaab se har jodi ka khel lambe samay me ghate ka hai (95 guna par 100 me 95 wapas). 30 jodi par ek poora khali din Rs 2,100 ka hota hai."))
 }).catch(e=>box.replaceChildren(el("div",{class:"warn"},"Pocket nahi aaye: "+e.message)));
 return box}
const old=tabs.monitor;
tabs.monitor=async function(m){m.append(await card());await old.call(tabs,m)};
})();
