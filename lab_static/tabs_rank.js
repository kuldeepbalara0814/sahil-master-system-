"use strict";
/* NUMBER RANK: aaj ke sab bane maps ke vote se number ranking */
(function(){
const LOCS=[["ALL","All location"],["FB","FB"],["GB","GB"],["GL","GL"],["DS","DS"]];
function copyText(txt){
 const fallback=()=>{const ta=el("textarea",{style:"position:fixed;left:-9999px;top:0;opacity:0",readonly:true});ta.value=txt;document.body.append(ta);ta.focus();ta.select();
  let ok=false;try{ok=document.execCommand("copy")}catch(e){}ta.remove();return ok};
 try{if(navigator.clipboard&&navigator.clipboard.writeText&&window.isSecureContext!==false)
  return navigator.clipboard.writeText(txt).then(()=>true,()=>fallback())}catch(e){}
 return Promise.resolve(fallback())}
async function doCopy(rows){
 const txt=rows.map(r=>p2(r.n)).join(" ");
 if(!txt){toast("Copy karne ko number nahi hai");return}
 const ok=await copyText(txt);toast(ok?"Copy ho gaya":"Copy nahi hua, dobara try karo")}
tabs.rank=async function(root){
 let rep=null,gk=null,loc="ALL";
 try{gk=localStorage.getItem("rk_g");loc=localStorage.getItem("rk_l")||"ALL"}catch(e){}
 const head=el("div",{class:"card"}),gsel=el("div",{class:"rk-seg"}),lsel=el("div",{class:"rk-seg"}),body=el("div");
 function save(){try{localStorage.setItem("rk_g",gk);localStorage.setItem("rk_l",loc)}catch(e){}}
 function draw(){
  const gs=rep.groups||[];if(!gs.find(g=>g.key===gk))gk=gs.length?gs[0].key:null;
  const g=gs.find(x=>x.key===gk);
  gsel.replaceChildren(...gs.map(x=>el("button",{type:"button",class:x.key===gk?"on":"",on:{click:()=>{gk=x.key;save();draw()}}},x.naam,el("small",{},` ${x.maps}`))));
  if(!g){lsel.replaceChildren();body.replaceChildren(el("p",{class:"mut"},"Aaj ke liye koi map nahi bana."));return}
  lsel.replaceChildren(...LOCS.map(([k,nm])=>el("button",{type:"button",class:k===loc?"on":"",on:{click:()=>{loc=k;save();draw()}}},nm,el("small",{},` ${((g.lists||{})[k]||[]).length}`))));
  const rows=(g.lists||{})[loc]||[],top=rows.reduce((a,r)=>Math.max(a,r.score),0)||1;
  const lname=(LOCS.find(x=>x[0]===loc)||[])[1];
  if(!rows.length){body.replaceChildren(el("div",{class:"card rk-empty"},el("b",{},`${g.naam} - ${lname}`),el("p",{class:"mut",style:"margin:6px 0 0"},"is location ke liye koi map nahi")));return}
  body.replaceChildren(el("div",{class:"card"},
   el("div",{class:"act-top"},el("b",{},`${g.naam} - ${lname}`),el("span",{class:"mut small"},`${rows.length} number | ${g.maps} map`)),
   el("div",{class:"row rk-btns"},el("button",{type:"button",class:"b sm",on:{click:()=>doCopy(rows)}},"Sab copy"),
    el("button",{type:"button",class:"b g sm",on:{click:()=>doCopy(rows.slice(0,10))}},"Top 10 copy")),
   rows.map((r,i)=>row(r,i,top))))}
 function row(r,i,top){
  const mp=r.maps||[],shown=mp.slice(0,4),more=mp.length-shown.length;
  return el("div",{class:"rk-row"},
   el("span",{class:"rk-no"},"#"+(i+1)),chip(r.n,i<3?"green":i<6?"yellow":"grey"),
   el("div",{class:"rk-mid"},
    el("div",{class:"rk-top"},el("b",{},String(r.score)),r.baar?el("span",{class:"act-tag"},"+2 din"):null,el("span",{class:"mut small"},`${r.votes} map`)),
    el("div",{class:"act-bar"},el("i",{style:`width:${Math.max(4,100*r.score/top)}%`})),
    mp.length?el("div",{class:"mut small rk-maps"},shown.join(", ")+(more>0?` +${more} aur`:"")):null))}
 root.append(head,el("div",{class:"rk-lbl mut small"},"Pattern type"),gsel,el("div",{class:"rk-lbl mut small"},"Location"),lsel,body,
  el("div",{class:"card flat"},el("b",{},"Ye kaise kaam karta hai"),el("p",{class:"mut small",style:"margin:6px 0 0"},"Ek map = ek vote. Score = kitne alag map ne ye number diya + dost ke point (pichli line ke har number ke 12 dost: 5 hara, 4 peela, 3 narangi; list me jitni baar aaya utne point) + 2 agar aaj ke din (baar) ki tokri me hai.")));
 body.replaceChildren(el("p",{class:"load"},el("span",{class:"spin"}),"Ranking ban rahi hai..."));
 try{rep=await api("GET","/rank")}catch(e){body.replaceChildren(el("div",{class:"warn"},e.message));return}
 head.replaceChildren(el("h2",{style:"margin:0 0 4px"},"Number Rank"),
  el("p",{class:"small",style:"margin:0"},el("b",{},`${rep.date||""} ${rep.weekday||""}`),el("span",{class:"mut"}," | Din ke 2 point: "),el("b",{},rep.weekday||"")),
  rep.scan_time?el("p",{class:"mut small",style:"margin:4px 0 0"},"Scan: "+String(rep.scan_time).replace("T"," ").slice(0,16)):null);
 draw()};
})();
