"use strict";
/* LAB: apna idea apni bhasha me likho -> samjho -> backtest */
(function(){
const BE=1/95,RND=0.01;
const EXAMPLES=["kal GB me jo aaya wahi aaj FB, GL aur DS me lagao","kal GB ka number aur uska palat aaj GL me","FB me 30 ke top 5 dost lagao",
 "pichle 30 din me sabse zyada aaye wo 10 number GB me","jo number sabse der se nahi aaya wo 10 number FB me","kal DS ka number +1 GB me shukravar ko","kal GB ke number ki family DS me"];
const LAGS=[[1,"kal (pichla din)"],[0,"aaj, pehle wale game ka"],[2,"parso (2 din pehle)"],[3,"3 din pehle"],[4,"4 din pehle"],[5,"5 din pehle"],[6,"6 din pehle"],[7,"7 din pehle"]];
const WD=["Som","Mangal","Budh","Guru","Shukra","Shani","Ravi"];
const OPN=[["same","wahi number"],["palat","palat"],["plus1","+1"],["minus1","-1"],["family","family (rashi+palat)"]];
const R=(x,d=2)=>(100*x).toFixed(d)+"%";
const rs=n=>(n>=0?"+":"")+Math.round(n).toLocaleString("en-IN")+" Rs";
const heat=h=>{const r=h/BE;return r>=1.1?"rgba(47,168,102,.38)":r>=.95?"rgba(226,177,0,.32)":"rgba(224,82,82,.30)"};
const tile=(k,v,s,cls)=>el("div",{class:"tile"},el("div",{class:"k"},k),el("div",{class:"v "+(cls||"")},v),s?el("div",{class:"s"},s):null);
const selOpts=(arr,val)=>arr.map(([v,l])=>{const o=el("option",{value:v},l);if(String(v)===String(val))o.selected=true;return o});
const gSel=v=>{const s=el("select",{},selOpts(Object.entries(GN),v));return s};

tabs.lab=async function(m){
 let cur=null,lastText="";
 const ta=el("textarea",{placeholder:"jaise: kal GB me jo aaya wahi aaj FB me lagao",maxlength:"400"});
 const understand=el("div"),result=el("div"),saved=el("div");
 const examples=el("div",{class:"chips"},EXAMPLES.map(t=>el("span",{class:"ex",on:{click:()=>{ta.value=t;doParse()}}},t)));
 m.append(el("div",{class:"card"},el("h2",{},"Idea Lab"),
  el("p",{class:"mut"},"Apna idea apni bhasha me likho. Computer use 13 saal ke result par test karke batayega ki chalta hai ya nahi. Koi khaas format nahi chahiye."),
  ta,el("div",{class:"row",style:"margin-top:8px"},el("button",{class:"b",on:{click:()=>doParse()}},"Samjho"),el("span",{class:"mut small"},"ya neeche se koi example dabao")),examples),
  understand,result,saved);

 async function doParse(){
  lastText=ta.value.trim();understand.replaceChildren();result.replaceChildren();
  if(!lastText)return toast("Pehle idea likho");
  try{const r=await api("POST","/lab/parse",{text:lastText});
   if(!r.ok){understand.append(el("div",{class:"card"},el("div",{class:"warn"},r.error)));return}
   cur=r.spec;showUnderstanding(r)}catch(e){understand.append(el("div",{class:"warn"},e.message))}}

 function showUnderstanding(r){
  const f=buildForm(cur);
  understand.replaceChildren(el("div",{class:"card"},el("h3",{style:"margin-top:0"},"Maine ye samjha:"),el("div",{class:"explain"},fb(r.explain)),
   r.ignored&&r.ignored.length?el("p",{class:"mut small"},"Ye shabd maine nahi liye: "+r.ignored.join(", ")):null,
   (r.warnings||[]).map(w=>el("p",{class:"warn small"},w)),
   el("details",{class:"fx"},el("summary",{},"Galat samjha? Yahan khud theek karo"),f.node),
   el("div",{class:"row",style:"margin-top:12px"},el("button",{class:"b big2",on:{click:()=>test(f.get())}},"Backtest karo"),
    el("span",{class:"mut small"},"Seedha sahi lagta hai to bas ye dabao"))));
 }

 function buildForm(s){
  const mode=el("select",{},selOpts([["rule","Pichle result ke number se"],["hot","Jo number sabse zyada aaye (hot)"],["cold","Jo number sabse der se nahi aaya (cold)"]],s.mode));
  const srcBox=el("div"),ruleBox=el("div"),hcBox=el("div");
  const addSrc=(g,l)=>{const gs=gSel(g),ls=el("select",{},selOpts(LAGS,l));const row=el("div",{class:"row",style:"margin:4px 0"},gs,ls,el("button",{class:"b g sm",on:{click:()=>row.remove()}},"hatao"));row._g=gs;row._l=ls;srcBox.append(row)};
  (s.sources||[{game:"GB",lag:1}]).forEach(x=>addSrc(x.game,x.lag));
  const value=el("input",{type:"number",min:"0",max:"99",placeholder:"koi bhi",style:"width:90px",value:s.value??""});
  const base=el("select",{},selOpts([["source","Source ka number"],["fixed","Mere diye number"]],s.base||"source"));
  const fixed=el("input",{placeholder:"jaise 30, 47",value:(s.fixed||[]).map(p2).join(", ")});
  const ops=OPN.map(([v,l])=>el("label",{class:"chk"},el("input",{type:"checkbox",value:v,checked:(s.ops||["same"]).includes(v)})," "+l));
  const dop=(s.ops||[]).find(o=>o.startsWith("dost"));
  const dchk=el("input",{type:"checkbox",checked:!!dop}),dn=el("select",{},[1,2,3,4,5,6,7,8,9,10].map(v=>{const o=el("option",{value:v},v);if(v===(dop?+dop.slice(4):3))o.selected=true;return o}));
  const win=el("input",{type:"number",min:"5",max:"365",value:s.window||30,style:"width:90px"}),topk=el("input",{type:"number",min:"1",max:"40",value:s.topk||10,style:"width:90px"});
  const on=Object.entries(GN).map(([k,v])=>el("label",{class:"chk"},el("input",{type:"checkbox",value:k,checked:(s.on||[]).includes(k)})," "+v));
  const days=WD.map((n,i)=>el("label",{class:"chk"},el("input",{type:"checkbox",value:i,checked:(s.days||[]).includes(i)})," "+n));
  ruleBox.append(el("label",{},"Number kahan se aayega? (kab ka kaun sa game)"),srcBox,el("button",{class:"b g sm",on:{click:()=>addSrc("GB",1)}},"+ aur source"),
   el("div",{class:"row",style:"margin-top:10px"},el("span",{},"Sirf tab jab wo number ho:"),value),
   el("div",{class:"row",style:"margin-top:10px"},el("span",{},"Base:"),base,fixed),
   el("div",{style:"margin-top:10px"},el("div",{class:"mut small"},"Kaun se number lagane hain:"),ops,el("span",{class:"chk"},dchk," uske top ",dn," dost")));
  hcBox.append(el("div",{class:"row"},el("span",{class:"hotonly"},"Pichle ",win," din"),el("span",{},"Top ",topk," number")));
  const refresh=()=>{ruleBox.style.display=mode.value==="rule"?"":"none";hcBox.style.display=mode.value==="rule"?"none":"";hcBox.querySelector(".hotonly").style.display=mode.value==="hot"?"":"none";fixed.style.display=base.value==="fixed"?"":"none"};
  mode.onchange=base.onchange=refresh;refresh();
  const node=el("div",{class:"fgrid"},el("label",{},"Idea ka type",mode),ruleBox,hcBox,
   el("div",{},el("div",{class:"mut small"},"Kis game me lagana hai:"),on),el("div",{},el("div",{class:"mut small"},"Kin din (khaali = roz):"),days));
  const get=()=>{const o={mode:mode.value,on:on.map(l=>l.firstChild).filter(i=>i.checked).map(i=>i.value),days:days.map(l=>l.firstChild).filter(i=>i.checked).map(i=>+i.value)};
   if(o.mode==="rule"){o.sources=[...srcBox.children].map(r=>({game:r._g.value,lag:+r._l.value}));o.base=base.value;
    if(value.value!=="")o.value=+value.value;
    if(o.base==="fixed")o.fixed=fixed.value.split(/[ ,]+/).filter(Boolean).map(Number);
    o.ops=ops.map(l=>l.firstChild).filter(i=>i.checked).map(i=>i.value);if(dchk.checked)o.ops.push("dost"+dn.value);
    if(o.base==="fixed"&&!o.sources.length)delete o.sources}
   else{o.topk=+topk.value;o.window=+win.value}
   return o};
  return {node,get};
 }

 async function test(spec){
  result.replaceChildren(el("div",{class:"card"},el("span",{class:"spin"}),"13 saal ke result par test chal raha hai... (kuch second)"));
  try{const r=await api("POST","/lab/test",{spec});cur=r.spec;showResult(r)}catch(e){result.replaceChildren(el("div",{class:"card"},el("div",{class:"warn"},e.message)))}
  result.scrollIntoView({behavior:"smooth",block:"start"});
 }

 function showResult(r){
  const x=r.result,s=x.summary,v=x.verdict,c=el("div");
  c.append(el("div",{class:"card"},el("h3",{style:"margin-top:0"},"Backtest ka natija"),el("div",{class:"explain"},fb(r.explain)),
   el("div",{class:"verdict "+v.color},el("h3",{},v.title),el("div",{},v.text)),
   s.bets?el("div",{class:"tiles"},
    tile("Kul bet",s.bets.toLocaleString("en-IN"),`roz ~${s.avg_n.toFixed(1)} number`),
    tile("Hit % (100 me)",R(s.hit_pct),`break-even ${R(BE)} | random ${R(RND)}`,s.hit_pct>=BE?"ok":"bad"),
    tile("95% range",R(s.ci_low)+" - "+R(s.ci_high),s.ci_low>RND?"random se upar, pakka":"random ko chhoo rahi"),
    tile("Paper ROI",(s.roi>=0?"+":"")+R(s.roi,1),`Rs5/number par ${rs(s.net)}`,s.roi>=0?"ok":"bad")):null));
  if(s.bets){
   const p=x.parts,rc=x.recent,box=(t,st,sub)=>tile(t,R(st.hit_pct),`${st.bets} bet | ROI ${(st.roi>=0?"+":"")+R(st.roi,0)}${sub?" | "+sub:""}`,st.hit_pct>=BE?"ok":"bad");
   c.append(el("div",{class:"card"},el("h3",{style:"margin-top:0"},"Kya ye aaj bhi chalta hai? (sabse zaroori)"),
    el("p",{class:"mut small"},"Purane saalon me chal gaya idea aaj nahi chalta ho sakta. Isliye data ko hisson me baant kar dekha."),
    el("div",{class:"tiles"},box("Pehle ka hissa (seekha)",p.seekha,p.seekha_range?p.seekha_range[0].slice(0,4)+"-"+p.seekha_range[1].slice(0,4):""),
     box("Baad ka hissa (parakha)",p.parakha,p.parakha_range?p.parakha_range[0].slice(0,4)+"-"+p.parakha_range[1].slice(0,4):""),
     box("Pichle 12 mahine",rc.last12m),box("Pichle 3 mahine",rc.last3m)),
    el("div",{class:"note small"},"Jitne zyada ideas try karoge, utna chance hai ki koi ek sirf kismat se achha dikhe. Isliye 'baad ka hissa' aur 'pichle 12 mahine' dono hare ho tabhi kuch maano.")));
   c.append(el("div",{class:"card"},el("h3",{style:"margin-top:0"},"Saal ke hisaab se"),
    el("table",{},el("thead",{},el("tr",{},["Saal","Bet","Hit %","ROI","Net"].map(t=>el("th",{},t)))),
     el("tbody",{},x.years.map(y=>el("tr",{},el("td",{},y.year),el("td",{},y.bets),el("td",{class:"heat",style:"background:"+heat(y.hit_pct)},R(y.hit_pct)),
      el("td",{class:y.roi>=0?"ok":"bad"},(y.roi>=0?"+":"")+R(y.roi,0)),el("td",{class:y.net>=0?"ok":"bad"},rs(y.net)))))),
    Object.keys(x.games).length>1?el("div",{},el("h3",{},"Game ke hisaab se"),el("table",{},el("thead",{},el("tr",{},["Game","Bet","Hit %","ROI"].map(t=>el("th",{},t)))),
     el("tbody",{},Object.entries(x.games).map(([g,y])=>el("tr",{},el("td",{},GN[g]),el("td",{},y.bets),el("td",{class:"heat",style:"background:"+heat(y.hit_pct)},R(y.hit_pct)),el("td",{class:y.roi>=0?"ok":"bad"},(y.roi>=0?"+":"")+R(y.roi,0))))))):null));
  }
  const t=x.today,tg=["FD","GB","GL","DS"].filter(g=>t[g]).map(g=>[g,t[g]]);
  const stake=el("select",{},[5,10,15,20].map(n=>el("option",{value:n},n+" Rs")));
  c.append(el("div",{class:"card"},el("h3",{style:"margin-top:0"},"Aaj ("+t.play_date+") ye idea kya lagayega?"),
   tg.map(([g,o])=>el("div",{class:"fr"},el("b",{style:"min-width:34px"},GN[g]),o.numbers.length?el("div",{class:"row"},o.numbers.map(n=>el("span",{class:"chip teal"},p2(n)))):el("span",{class:"mut"},o.why||"Abhi koi number nahi"))),
   tg.some(([g,o])=>o.numbers.length)?el("div",{class:"row",style:"margin-top:10px"},stake,el("button",{class:"b",on:{click:async()=>{let n=0;
     try{for(const [g,o] of tg)if(o.numbers.length){const q=await api("POST","/paper/place",{strategy:"manual",numbers:o.numbers,games:[g],stake:+stake.value});n+=q.added}toast(n+" paper bet lagi")}catch(e){toast(e.message)}}}},"Paper bet lagao")):null));
  const nm=el("input",{value:fb(r.explain).slice(0,70),style:"width:100%"});
  c.append(el("div",{class:"card"},el("h3",{style:"margin-top:0"},"Ye idea save karo"),nm,
   el("div",{class:"row",style:"margin-top:8px"},el("button",{class:"b",on:{click:async()=>{try{await api("POST","/lab/save",{spec:r.spec,text:lastText,name:nm.value,
     summary:{bets:s.bets,hit_pct:s.hit_pct,roi:s.roi,color:v.color,asof:r.asof}});toast("Idea save ho gaya");loadSaved()}catch(e){toast(e.message)}}}},"Save"),
    el("span",{class:"mut small"},"(PIN lagega)"))));
  result.replaceChildren(...c.childNodes);
 }

 async function loadSaved(){
  let L=[];try{L=await api("GET","/lab/ideas")}catch(e){}
  saved.replaceChildren(el("div",{class:"card"},el("h2",{},"Mere save kiye idea"),
   L.length?L.map(i=>el("div",{class:"idea"},el("div",{class:"nm"},el("div",{},fb(i.name)),el("div",{class:"mut small"},i.saved.slice(0,10)+(i.summary?` | hit ${R(i.summary.hit_pct)} | ROI ${(i.summary.roi>=0?"+":"")+R(i.summary.roi,0)}`:""))),
    i.summary?el("span",{class:"st "+(i.summary.color==="kam"?"kam":i.summary.color)},{hara:"hara",peela:"peela",laal:"laal",kam:"kam data"}[i.summary.color]):null,
    el("button",{class:"b g sm",on:{click:()=>{cur=i.spec;ta.value=i.text||"";understand.replaceChildren();showUnderstanding({explain:i.name,ignored:[],warnings:[]});test(i.spec)}}},"Dobara test"),
    el("button",{class:"b g sm",on:{click:async()=>{try{await api("POST","/lab/delete",{id:i.id});loadSaved()}catch(e){toast(e.message)}}}},"Hatao"))):
    el("p",{class:"mut"},"Abhi koi idea save nahi. Test ke baad 'Save' dabao.")));
 }
 loadSaved();
};
})();
