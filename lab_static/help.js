"use strict";
/* SAHIL LAB HELP (chatbot, Phase 1: sirf sawaal-jawaab). Har tab par neeche-right robot button.
   Browser Sarvam ko seedha call nahi karta: sirf apne server (/api/help) ko. API key browser me kabhi nahi aati (server env SARVAM_API_KEY).
   Chat sirf password se khulta hai; jaanch server par hoti hai. Password sirf is tab ke sessionStorage me rehta hai (tab band = bhool jata hai). */
(function(){
const SS={get(k){try{return sessionStorage.getItem(k)||""}catch(e){return ""}},set(k,v){try{sessionStorage.setItem(k,v)}catch(e){}},del(k){try{sessionStorage.removeItem(k)}catch(e){}}};
const NS="http://www.w3.org/2000/svg";
function robot(){const s=document.createElementNS(NS,"svg");s.setAttribute("viewBox","0 0 24 24");s.setAttribute("aria-hidden","true");
 const p=document.createElementNS(NS,"path");
 p.setAttribute("d","M12 2v3 M7 8h10a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-6a3 3 0 0 1 3-3z M9.5 13h.01 M14.5 13h.01 M9 17h6 M2 13h2 M20 13h2");
 s.append(p);return s}
let isOpen=false,busy=false,hist=[],cfg=null;
const body=el("div",{class:"hb-body"}),foot=el("div",{class:"hb-foot"});
const panel=el("div",{class:"hb-panel",role:"dialog","aria-label":"Sahil Lab Help",style:"display:none"},
 el("div",{class:"hb-head"},el("b",{},"Sahil Lab Help"),el("span",{class:"hb-sub"},"app ke baare me poochho"),
  el("span",{class:"hb-acts"},
   el("button",{type:"button",class:"hb-x",title:"Naya chat",on:{click:()=>{hist=[];SS.get("hb_pin")?chatView():start()}}},"↺"),
   el("button",{type:"button",class:"hb-x",title:"Lock (password bhool jao)",on:{click:()=>{SS.del("hb_pin");hist=[];start()}}},"🔒"),
   el("button",{type:"button",class:"hb-x",title:"Band karo","aria-label":"Band karo",on:{click:()=>toggle(false)}},"✕"))),
 body,foot);
const fab=el("button",{type:"button",class:"hb-fab","aria-label":"Sahil Lab Help kholo",title:"Sahil Lab Help",on:{click:()=>toggle()}},robot());
function toggle(v){isOpen=v===undefined?!isOpen:v;panel.style.display=isOpen?"flex":"none";fab.classList.toggle("on",isOpen);if(isOpen)start()}
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&isOpen)toggle(false)});
const bubble=(who,txt)=>{const b=el("div",{class:"hb-msg "+who});b.textContent=txt;body.append(b);body.scrollTop=body.scrollHeight;return b};
function note(txt,cls){body.replaceChildren(el("div",{class:"hb-note "+(cls||"")},txt));foot.replaceChildren()}

async function start(){
 note("Load ho raha hai...");
 try{cfg=await api("GET","/help/status")}catch(e){note("Abhi help se jud nahi paya. Dobara try karo.","bad");return}
 if(!cfg.key_set){note("API key set nahi hai — Render dashboard me SARVAM_API_KEY set karo.","bad");return}
 if(!cfg.pin_set){note("Help ka password set nahi hai — Render dashboard me HELP_PIN set karo.","bad");return}
 if(!SS.get("hb_pin")){pinView();return}
 chatView()}

function pinView(msg){
 const inp=el("input",{type:"password",inputmode:"numeric",autocomplete:"off",maxlength:"12",placeholder:"password",class:"hb-pin","aria-label":"Help password"});
 const err=el("div",{class:"hb-err"},msg||"");
 const go=async()=>{const pin=inp.value.trim();if(!pin)return;go.b.disabled=true;
  try{await api("POST","/help/unlock",{pin});SS.set("hb_pin",pin);chatView()}catch(e){err.textContent=e.message;inp.value="";inp.focus()}finally{go.b.disabled=false}};
 inp.addEventListener("keydown",e=>{if(e.key==="Enter")go()});
 go.b=el("button",{type:"button",class:"b",on:{click:go}},"Kholo");
 body.replaceChildren(el("div",{class:"hb-lock"},el("div",{class:"hb-big"},"🔒"),el("p",{},"Ye chat password se khulta hai."),inp,go.b,err));foot.replaceChildren();
 setTimeout(()=>inp.focus&&inp.focus(),50)}

function chatView(){
 body.replaceChildren();
 bubble("bot","Namaste! Mai Sahil Lab Help hu. App ke tab, pattern (Naksha, Family, 009...), niyam ya data ke baare me Hinglish me poochho. Mai sirf samjhata hu, kuch badalta nahi.");
 const ta=el("textarea",{rows:"2",maxlength:"400",placeholder:"Apna sawaal likho...","aria-label":"Sawaal"});
 const send=el("button",{type:"button",class:"b",on:{click:()=>ask(ta,send)}},"Bhejo");
 ta.addEventListener("keydown",e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();ask(ta,send)}});
 foot.replaceChildren(ta,send);setTimeout(()=>ta.focus&&ta.focus(),50)}

async function ask(ta,send){
 const q=ta.value.trim();if(!q||busy)return;busy=true;send.disabled=true;ta.value="";
 bubble("user",q);const wait=bubble("bot wait","soch raha hai...");
 try{const r=await api("POST","/help",{question:q,history:hist.slice(-4),pin:SS.get("hb_pin")});
  wait.className="hb-msg bot";wait.textContent=r.answer;
  if(r.via==="faq"||r.via==="cache")wait.append(el("div",{class:"hb-via"},r.via==="faq"?"⚡ taiyar jawab (bina AI ke, token nahi laga)":"⚡ pehle ka jawab (token nahi laga)"));
  hist.push({role:"user",content:q},{role:"assistant",content:r.answer});hist=hist.slice(-4)}
 catch(e){wait.className="hb-msg bot bad";wait.textContent=e.message;
  if(/PIN galat|password/i.test(e.message)){SS.del("hb_pin");setTimeout(()=>pinView(e.message),600)}}
 finally{busy=false;send.disabled=false;body.scrollTop=body.scrollHeight;ta.focus&&ta.focus()}}

document.body.append(panel,fab);
})();
