"use strict";

const $=(s,r=document)=>r.querySelector(s);
function el(t,a,...k){if(a===null||typeof a!=="object"||a instanceof Node||Array.isArray(a)){k.unshift(a);a={}}
 const e=document.createElement(t);for(const[x,v]of Object.entries(a)){if(x==="class")e.className=v;else if(x==="on")for(const[ev,fn]of Object.entries(v))e.addEventListener(ev,fn);else if(v!==undefined&&v!==null&&v!==false)e.setAttribute(x,v===true?"":v)}
 for(const c of k.flat())if(c!==undefined&&c!==null&&c!==false)e.append(c instanceof Node?c:String(c));return e}
const p2=n=>String(n).padStart(2,"0");
const pct=(x,d=1)=>(100*x).toFixed(d)+"%";
let ST={};
function toast(m){const t=$("#toast");t.textContent=m;t.style.display="block";clearTimeout(toast.t);toast.t=setTimeout(()=>t.style.display="none",4200)}
async function api(method,path,body,retry=true){
 const h={"Content-Type":"application/json"};let pin="";try{pin=localStorage.getItem("pin")||""}catch(e){}
 if(pin)h["X-Admin-Pin"]=pin;
 const r=await fetch("/api"+path,{method,headers:h,body:body?JSON.stringify(body):undefined});
 let j={};try{j=await r.json()}catch(e){}
 if(r.status===401&&retry){const x=prompt("Likhne ke liye PIN dalo:");if(x){try{localStorage.setItem("pin",x)}catch(e){}return api(method,path,body,false)}}
 if(!r.ok)throw new Error(j.error||("Galti "+r.status));return j}
const chip=(n,tier,extra)=>el("span",{class:"chip "+(tier||"grey")+(extra?" "+extra:"")},p2(n));
function tiers(i,total){return i<3?"green":i<6?"yellow":"orange"}
const LEGEND=()=>el("div",{class:"legend mut"},el("span",{},el("span",{class:"chip green",style:"font-size:12px;min-width:0;padding:1px 7px"},"HARA")," sabse zyada chance (top 3)"),
 el("span",{},el("span",{class:"chip yellow",style:"font-size:12px;min-width:0;padding:1px 7px"},"PEELA")," beech ke"),el("span",{},el("span",{class:"chip orange",style:"font-size:12px;min-width:0;padding:1px 7px"},"NARANGI")," kam chance (last 4)"));

const GN={FD:"FB",GB:"GB",GL:"GL",DS:"DS"};
const fb=s=>String(s).replace(/\bFD\b/g,"FB");
const tabs={};
const ICONS={dost:"M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75",
 aaj:"M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2 M9 3h6v4H9z M9 12h6 M9 16h6",
 lab:"M10 2v7.5L4.5 19a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 9.5V2 M8.5 2h7 M7 16h10",
 paper:"M3 17l6-6 4 4 8-8 M15 7h6v6",monitor:"M22 12h-4l-3 9L9 3l-3 9H2",
 record:"M3 3h18v18H3z M3 9h18 M3 15h18 M9 3v18",
 data:"M12 8c4.4 0 8-1.3 8-3s-3.6-3-8-3-8 1.3-8 3 3.6 3 8 3z M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5 M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
 guide:"M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"};
const NAMES={dost:"Dost Khojo",aaj:"Aaj ki List",lab:"Lab",paper:"Paper Trading",monitor:"Monitor",record:"Record",data:"Data",guide:"Guide"};
function icon(k){const s=document.createElementNS("http://www.w3.org/2000/svg","svg");s.setAttribute("viewBox","0 0 24 24");const p=document.createElementNS("http://www.w3.org/2000/svg","path");p.setAttribute("d",ICONS[k]);s.append(p);return s}
async function go(t){
 try{localStorage.setItem("tab",t)}catch(e){}
 document.querySelectorAll("#nav button").forEach(b=>b.classList.toggle("on",b.dataset.t===t));
 const my=go.n=(go.n||0)+1,m=$("#main"),tmp=el("div");m.replaceChildren(el("p",{class:"mut"},el("span",{class:"spin"}),"Load ho raha hai..."));
 try{await tabs[t](tmp);if(my===go.n)m.replaceChildren(...tmp.childNodes)}catch(e){if(my===go.n)m.replaceChildren(el("div",{class:"warn"},e.message))}
 window.scrollTo({top:0})}
function boot(){
 for(const k of Object.keys(NAMES))$("#nav").append(el("button",{"data-t":k,on:{click:()=>go(k)}},icon(k),NAMES[k]));
 let first="dost";try{const t=localStorage.getItem("tab");if(t&&NAMES[t])first=t}catch(e){}
 fetch("/api/status").then(r=>r.json()).then(s=>{ST=s;$("#meta").textContent=`${s.days} din | aakhri ${s.last_date}`}).catch(()=>{$("#meta").textContent=""}).finally(()=>go(first))}
