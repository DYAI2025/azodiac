#!/usr/bin/env python3
"""Generate a single-file editable architecture HTML from architecture JSON.

Usage:
  python scripts/generate_architecture_editor.py --input architecture.json --output architecture-editor.html
  python scripts/generate_architecture_editor.py --output architecture-editor.html
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


def sample_model() -> dict[str, Any]:
    return {
        "project": {
            "name": "Architecture Editor",
            "domain": "mixed",
            "repo": "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "description": "Generated editable architecture model.",
        },
        "nodes": [
            {"id": "entry", "x": 180, "y": 180, "type": "entry", "icon": "◎", "label": "Entry", "sub": "request", "detail": {"title": "Entry", "subtitle": "entry", "tags": ["entry"], "flow": ["Receive request"], "apis": [], "schemas": [], "notes": "", "constraints": [], "risks": []}},
            {"id": "service", "x": 520, "y": 180, "type": "service", "icon": "▣", "label": "Service", "sub": "logic", "detail": {"title": "Service", "subtitle": "application logic", "tags": ["api"], "flow": ["Process request"], "apis": [{"method": "GET", "path": "/api/example", "desc": "Example endpoint", "params": ["id: string"]}], "schemas": [], "notes": "", "constraints": [], "risks": []}},
        ],
        "edges": [{"from": "entry", "to": "service", "style": "primary", "relation": "api-call", "label": "calls"}],
        "changes": [],
    }


def load_model(path: str | None) -> dict[str, Any]:
    model = sample_model() if not path else json.loads(Path(path).read_text(encoding="utf-8"))
    model.setdefault("project", {})
    model.setdefault("nodes", [])
    model.setdefault("edges", [])
    model.setdefault("changes", [])
    return model


HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__ · Architecture Editor</title><style>
body{margin:0;background:#08090d;color:#f0e6c8;font-family:ui-monospace,Menlo,Consolas,monospace;overflow:hidden}header{position:fixed;top:0;left:0;right:0;height:58px;display:flex;justify-content:space-between;align-items:center;padding:8px 14px;background:#08090df7;border-bottom:1px solid #c9a84c44;z-index:5}h1{font-size:15px;color:#c9a84c;margin:0}button{background:#111827;color:#f0e6c8;border:1px solid #c9a84c66;border-radius:5px;padding:6px 9px;margin:2px;cursor:pointer}button:hover{color:#e8c97a;border-color:#e8c97a}#canvas{position:fixed;inset:58px 380px 0 0;overflow:auto}#scene{position:relative;width:1600px;height:1000px}svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.node{position:absolute;transform:translate(-50%,-50%);min-width:130px;background:#111827ee;border:1px solid #c9a84c66;border-radius:8px;padding:10px;text-align:center;cursor:pointer}.node:hover,.active{border-color:#e8c97a}.node.health-green{border-color:#2dff7a;background:#10251bee}.node.health-yellow{border-color:#ffd35a;background:#2b2410ee}.node.health-red{border-color:#ff5c5c;background:#2b1010ee}.node.health-unknown{border-color:#8a7f9a}.status{display:inline-block;border-radius:99px;padding:2px 7px;margin:2px;font-size:11px}.status.green{background:#12351f;color:#7dffab}.status.yellow{background:#3a2d08;color:#ffe08a}.status.red{background:#3a1111;color:#ff9a9a}.status.unknown{background:#24202d;color:#c8bfd8}.modified:after{content:'●';position:absolute;right:5px;top:3px;color:#c9a84c}.deleted{opacity:.4;text-decoration:line-through}.icon{font-size:21px;display:block}.sub{display:block;color:#8a7f9a;font-size:11px}#panel{position:fixed;right:0;top:58px;bottom:0;width:380px;background:#0d0f16f8;border-left:1px solid #c9a84c44;overflow:auto;padding:14px}.card{border-bottom:1px solid #ffffff18;padding:10px 0}.tag{display:inline-block;border:1px solid #77a7ff77;border-radius:99px;padding:2px 6px;margin:2px;font-size:11px}textarea,input,select{width:100%;box-sizing:border-box;background:#08090d;color:#f0e6c8;border:1px solid #c9a84c55;border-radius:5px;padding:6px;margin:4px 0 8px}textarea{min-height:90px}#modal{display:none;position:fixed;inset:7%;background:#08090d;border:1px solid #c9a84c77;z-index:10;box-shadow:0 0 80px #000}#modal.open{display:flex;flex-direction:column}#modal textarea{flex:1;border:0;border-top:1px solid #ffffff22;border-radius:0;margin:0;padding:16px;white-space:pre}.row{border:1px solid #ffffff18;border-radius:6px;padding:7px;margin:6px 0}.muted{color:#8a7f9a;font-size:12px}.legend{position:fixed;left:14px;bottom:14px;background:#0d0f16f2;border:1px solid #c9a84c66;border-radius:8px;padding:10px;z-index:6;min-width:280px}.legend h3{margin:0 0 6px 0;font-size:13px;color:#e8c97a}.legend-item{display:flex;align-items:center;gap:8px;font-size:12px;margin:4px 0}.line-sample{width:36px;height:0;border-top:2px solid #c9a84c99}.line-sample.dashed{border-top-style:dashed}.line-sample.primary{border-top-color:#77a7ffcc}.line-sample.secondary{border-top-color:#c9a84c99}.line-sample.event{border-top-color:#b68cffcc}.node.deviation{border-color:#ff5c5c!important;box-shadow:0 0 0 2px #ff5c5c55}.deviation-note{margin-top:8px;padding:8px;border:1px solid #ff5c5c77;background:#2b1010aa;border-radius:6px}.deviation-edge{stroke:#ff5c5c!important;stroke-width:2.2!important}.deviation-badge{display:inline-block;margin-left:6px;padding:2px 6px;border:1px solid #ff5c5c77;border-radius:99px;color:#ffb3b3;font-size:10px}</style></head><body>
<header><div><h1 id="title"></h1><div class="muted">editable architecture → dev brief → full snapshot</div></div><div><button onclick="toggleEdit()" id="editBtn">EDIT MODE</button><button onclick="addNode()">ADD NODE</button><button onclick="saveLocal()">SAVE</button><button onclick="loadLocal()">LOAD</button><button onclick="downloadJSON()">EXPORT DATA</button><button onclick="runHealthCheck()">CHECK LIVE API</button><button onclick="validateArchitecture()">VALIDATE ARCH</button><button onclick="exportDeviationBrief()">EXPORT DEVIATIONS</button><button onclick="triggerAutoImprove()">AUTO-IMPROVE</button><button onclick="confirmAutoImprove()">CONFIRM AI</button><button onclick="showBrief()">EXPORT CHANGES</button><button onclick="showSnapshot()">EXPORT ALL STATES</button></div></header>
<div id="canvas"><div id="scene"><svg id="lines"></svg></div></div><div class="legend"><h3>Legend</h3><div class="legend-item"><span class="line-sample primary"></span>Primary API / critical flow</div><div class="legend-item"><span class="line-sample secondary"></span>Dependency / relation</div><div class="legend-item"><span class="line-sample dashed"></span>API/Event/Data logical link</div><div class="legend-item"><span class="line-sample event dashed"></span>Event stream / async</div><div class="legend-item"><span class="status green">GREEN</span>Healthy</div><div class="legend-item"><span class="status yellow">YELLOW</span>Partial issue</div><div class="legend-item"><span class="status red">RED</span>Broken or deviation</div><div class="legend-item"><span class="status unknown">UNKNOWN</span>Not checked</div></div><aside id="panel">Select a node.</aside><div id="modal"><header style="position:static"><h1 id="modalTitle"></h1><div><button onclick="copyModal()">COPY</button><button onclick="downloadModal()">DOWNLOAD</button><button onclick="closeModal()">CLOSE</button></div></header><textarea id="modalText"></textarea></div>
<script id="data" type="application/json">__MODEL_JSON__</script><script>
const dom = { data: document.getElementById('data'), title: document.getElementById('title'), scene: document.getElementById('scene'), lines: document.getElementById('lines'), panel: document.getElementById('panel'), modal: document.getElementById('modal'), modalTitle: document.getElementById('modalTitle'), modalText: document.getElementById('modalText'), editBtn: document.getElementById('editBtn') };
let model=JSON.parse(dom.data.textContent),map={},active=null,edit=false,fileName='architecture.md';
const E=s=>String(s??'').replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const now=()=>new Date().toISOString();
function rebuild(){map=Object.fromEntries((model.nodes||[]).map(n=>[n.id,n]));}
function change(c){model.changes=model.changes||[];model.changes.push({id:'c_'+Math.random().toString(36).slice(2,9),timestamp:now(),...c});render();}
function render(){rebuild();dom.title.textContent=(model.project?.name||'Architecture')+' · '+(model.changes?.length||0)+' changes';dom.scene.querySelectorAll('.node').forEach(n=>n.remove());(model.nodes||[]).forEach(n=>{let el=document.createElement('div'),hs=nodeHealth(n.id).status;let dev=nodeDeviation(n.id);el.className='node health-'+hs+' '+(dev?'deviation ':'')+(n._deleted?'deleted ':'')+((model.changes||[]).some(c=>c.nodeId===n.id)?'modified':'');el.style.left=n.x+'px';el.style.top=n.y+'px';el.onclick=()=>openNode(n.id);el.innerHTML=`<span class="icon">${E(n.icon||'◇')}</span>${E(n.label||n.id)}<span class="sub">${E(n.sub||n.type||'')}</span>`;dom.scene.appendChild(el)});drawEdges();if(active)openNode(active)}
function drawEdges(){dom.lines.innerHTML='';(model.edges||[]).forEach(e=>{let a=map[e.from],b=map[e.to];if(!a||!b)return;let p=document.createElementNS('http://www.w3.org/2000/svg','path'),dx=b.x-a.x;p.setAttribute('d',`M ${a.x} ${a.y} C ${a.x+dx*.45} ${a.y}, ${b.x-dx*.45} ${b.y}, ${b.x} ${b.y}`);p.setAttribute('fill','none');p.setAttribute('stroke',edgeColor(e));p.setAttribute('stroke-width','1.4');if(['api','event','data'].includes(e.style))p.setAttribute('stroke-dasharray','5 5');if(edgeDeviation(e))p.setAttribute('class','deviation-edge');dom.lines.appendChild(p)})}
function row(x){return `<div class="row">${x}</div>`}
function openNode(id){active=id;let n=map[id],d=n.detail||{},h=nodeHealth(id);dom.panel.innerHTML=`<div class="card"><h2>${E(d.title||n.label||id)}${nodeDeviation(id)?'<span class="deviation-badge">DEVIATION</span>':''}</h2><div><span class="status ${h.status}">${E(h.status.toUpperCase())}</span><span class="muted">${E(h.summary||'not checked')}</span></div><div class="muted">${E(d.subtitle||n.type||'component')}</div>${(d.tags||[]).map(t=>`<span class="tag">${E(t)}</span>`).join('')}<p>${E(d.notes||'')}</p>${nodeDeviation(id)?`<div class="deviation-note"><b>Deviation:</b> ${E(nodeDeviation(id).message)}<br><button onclick="draftDeviationForNode('`+id+`')">Create Dev Brief</button></div>`:''}${edit?'<button onclick="editNode()">EDIT NODE</button><button onclick="deleteNode()">DELETE NODE</button>':''}</div><div class="card"><b>Flow</b>${(d.flow||[]).map((s,i)=>row(`${i+1}. ${E(s)} ${edit?`<button onclick="editFlow(${i})">edit</button><button onclick="deleteFlow(${i})">del</button>`:''}`)).join('')}${edit?'<button onclick="addFlow()">ADD FLOW</button>':''}</div><div class="card"><b>API Routes</b>${(d.apis||[]).map((a,i)=>{let ah=apiHealth(id,i);return row(`<span class="status ${ah.status}">${E(ah.status.toUpperCase())}</span> <code>${E(a.method)} ${E(a.path)}</code><br>${E(a.desc||'')}<br><span class="muted">${E(ah.summary||'not checked')}</span> ${edit?`<button onclick="editApi(${i})">edit</button><button onclick="deleteApi(${i})">del</button>`:''}`)}).join('')}${edit?'<button onclick="addApi()">ADD API</button>':''}</div><div class="card"><b>Edges</b>${(model.edges||[]).map((e,i)=>({...e,i})).filter(e=>e.from===id||e.to===id).map(e=>row(`${E(e.from)} → ${E(e.to)} · ${E(e.relation||e.style||'edge')} ${edit?`<button onclick="rerouteEdge(${e.i})">reroute</button><button onclick="deleteEdge(${e.i})">del</button>`:''}`)).join('')}${edit?'<button onclick="addEdge()">ADD EDGE</button>':''}</div>`;}
function toggleEdit(){edit=!edit;dom.editBtn.textContent=edit?'EDIT MODE ON':'EDIT MODE';render()}
function form(h){dom.panel.insertAdjacentHTML('afterbegin',`<div class="card">${h}</div>`)}
function editNode(){let n=map[active],d=n.detail;form(`<input id=f_label value="${E(n.label)}"><input id=f_sub value="${E(n.sub)}"><input id=f_title value="${E(d.title)}"><input id=f_subtitle value="${E(d.subtitle)}"><textarea id=f_notes>${E(d.notes||'')}</textarea><input id=f_tags value="${E((d.tags||[]).join(', '))}"><button onclick="saveNode()">SAVE</button>`)}
function saveNode(){let n=map[active],before=JSON.parse(JSON.stringify(n));n.label=document.getElementById('f_label').value;n.sub=document.getElementById('f_sub').value;n.detail.title=document.getElementById('f_title').value;n.detail.subtitle=document.getElementById('f_subtitle').value;n.detail.notes=document.getElementById('f_notes').value;n.detail.tags=document.getElementById('f_tags').value.split(',').map(x=>x.trim()).filter(Boolean);change({type:'modify',target:'node',origin:'user-edit',nodeId:active,before,after:JSON.parse(JSON.stringify(n)),description:'Modified node '+active})}
function addFlow(){form(`<textarea id=f_flow></textarea><button onclick="saveNewFlow()">ADD</button>`)}function saveNewFlow(){let n=map[active];n.detail.flow=n.detail.flow||[];n.detail.flow.push(document.getElementById('f_flow').value);change({type:'add',target:'flow',origin:'user-edit',nodeId:active,after:document.getElementById('f_flow').value,description:'Added flow step to '+active})}
function editFlow(i){form(`<textarea id=f_flow>${E(map[active].detail.flow[i])}</textarea><button onclick="saveFlow(${i})">SAVE</button>`)}function saveFlow(i){let n=map[active],before=n.detail.flow[i];n.detail.flow[i]=document.getElementById('f_flow').value;change({type:'modify',target:'flow',origin:'user-edit',nodeId:active,before,after:document.getElementById('f_flow').value,description:'Modified flow step '+(i+1)+' of '+active})}function deleteFlow(i){let n=map[active],before=n.detail.flow.splice(i,1)[0];change({type:'delete',target:'flow',origin:'user-edit',nodeId:active,before,description:'Deleted flow step from '+active})}
function apiEditor(a={method:'GET',path:'',desc:'',params:[]},cb='saveNewApi()'){form(`<select id=f_method>${['GET','POST','PUT','PATCH','DELETE'].map(m=>`<option ${m===a.method?'selected':''}>${m}</option>`).join('')}</select><input id=f_path value="${E(a.path)}" placeholder="/api/path"><textarea id=f_desc>${E(a.desc||'')}</textarea><textarea id=f_params>${E((a.params||[]).join('\n'))}</textarea><button onclick="${cb}">SAVE</button>`)}
function readApi(){return{method:document.getElementById('f_method').value,path:document.getElementById('f_path').value,desc:document.getElementById('f_desc').value,params:document.getElementById('f_params').value.split('\n').map(x=>x.trim()).filter(Boolean)}}function addApi(){apiEditor()}function saveNewApi(){let n=map[active],a=readApi();n.detail.apis=n.detail.apis||[];n.detail.apis.push(a);change({type:'add',target:'api',origin:'user-edit',nodeId:active,after:a,description:'Added API '+a.method+' '+a.path+' to '+active})}function editApi(i){apiEditor(map[active].detail.apis[i],`saveApi(${i})`)}function saveApi(i){let n=map[active],before=JSON.parse(JSON.stringify(n.detail.apis[i])),a=readApi();n.detail.apis[i]=a;change({type:'modify',target:'api',origin:'user-edit',nodeId:active,before,after:a,description:'Modified API '+before.method+' '+before.path+' to '+a.method+' '+a.path})}function deleteApi(i){let n=map[active],before=n.detail.apis.splice(i,1)[0];change({type:'delete',target:'api',origin:'user-edit',nodeId:active,before,description:'Deleted API '+before.method+' '+before.path+' from '+active})}
function addNode(){let id=prompt('New node id in kebab-case');if(!id||map[id])return;let n={id,x:250+model.nodes.length*60,y:480,type:'custom',icon:'◇',label:id,sub:'',detail:{title:id,subtitle:'custom',tags:[],flow:[],apis:[],schemas:[],notes:'',constraints:[],risks:[]}};model.nodes.push(n);change({type:'add',target:'node',origin:'user-edit',nodeId:id,after:n,description:'Added node '+id})}function deleteNode(){let n=map[active],before=JSON.parse(JSON.stringify(n));n._deleted=true;change({type:'delete',target:'node',origin:'user-edit',nodeId:active,before,description:'Marked node '+active+' for deletion'})}
function addEdge(){let to=prompt('Target node id');if(!to||!map[to])return;let e={from:active,to,style:'secondary',relation:'dependency',label:''};model.edges.push(e);change({type:'add',target:'edge',origin:'user-edit',nodeId:active,after:e,description:'Added edge '+active+' to '+to})}function rerouteEdge(i){let e=model.edges[i],to=prompt('New target node id',e.to);if(!to||!map[to])return;let before=JSON.parse(JSON.stringify(e));e.to=to;change({type:'reroute',target:'edge',origin:'user-edit',edgeIndex:i,nodeId:active,before,after:JSON.parse(JSON.stringify(e)),description:'Rerouted edge '+before.from+' to '+before.to+' into '+e.from+' to '+e.to})}function deleteEdge(i){let before=model.edges.splice(i,1)[0];change({type:'delete',target:'edge',origin:'user-edit',edgeIndex:i,before,description:'Deleted edge '+before.from+' to '+before.to})}


function expectedById(){return Object.fromEntries((model.expectedArchitecture?.nodes||[]).map(n=>[n.id,n]))}
function nodeDeviation(id){let d=model.deviations?.nodes?.[id];return d&&d.status==='red'?d:null}
function edgeDeviation(e){let k=e.from+'->'+e.to;let d=model.deviations?.edges?.[k];return d&&d.status==='red'}
function validateArchitecture(){let expected=model.expectedArchitecture;if(!expected||!Array.isArray(expected.nodes)){alert('No expectedArchitecture baseline found in model. Add model.expectedArchitecture first.');return}let actual=Object.fromEntries((model.nodes||[]).filter(n=>!n._deleted).map(n=>[n.id,n]));let exp=Object.fromEntries((expected.nodes||[]).map(n=>[n.id,n]));let dev={nodes:{},edges:{},summary:{}};Object.keys(exp).forEach(id=>{if(!actual[id])dev.nodes[id]={status:'red',message:'Expected node missing in rendered architecture.'};else{let dif=[];if(exp[id].type&&actual[id].type!==exp[id].type)dif.push('type expected '+exp[id].type+' but got '+actual[id].type);let eApis=(exp[id].detail?.apis||[]).map(a=>String(a.method||'GET').toUpperCase()+' '+String(a.path||''));let aApis=(actual[id].detail?.apis||[]).map(a=>String(a.method||'GET').toUpperCase()+' '+String(a.path||''));eApis.forEach(ep=>{if(!aApis.includes(ep))dif.push('missing endpoint '+ep)});if(dif.length)dev.nodes[id]={status:'red',message:dif.join('; ')}}});Object.keys(actual).forEach(id=>{if(!exp[id])dev.nodes[id]={status:'red',message:'Unexpected node exists in rendered architecture.'}});let expEdges=new Set((expected.edges||[]).map(e=>e.from+'->'+e.to));let actEdges=new Set((model.edges||[]).map(e=>e.from+'->'+e.to));expEdges.forEach(k=>{if(!actEdges.has(k))dev.edges[k]={status:'red',message:'Expected edge missing: '+k}});actEdges.forEach(k=>{if(!expEdges.has(k))dev.edges[k]={status:'red',message:'Unexpected edge exists: '+k}});let total=Object.keys(dev.nodes).length+Object.keys(dev.edges).length;dev.summary={status:total?'red':'green',deviationCount:total,message:total?'Architecture deviations found: '+total:'No deviations found'};model.deviations=dev;change({type:'validate',target:'architecture',after:dev,description:'Validated expected architecture vs rendered architecture'});alert(dev.summary.message)}
function deviationBrief() {
  const d = model.deviations || {};
  const n = d.nodes || {};
  const e = d.edges || {};
  const rows = [];

  Object.entries(n).forEach(([id, v]) => rows.push(`- Node ${id}: ${v.message}`));
  Object.entries(e).forEach(([id, v]) => rows.push(`- Edge ${id}: ${v.message}`));

  if (!rows.length) {
    return `# Development Brief: No Deviations\n\nNo deviations available.`;
  }

  return `# Development Brief: Architecture Deviations\n\n## Summary\n${d.summary?.message || ''}\n\n## Deviations\n${rows.join('\n')}\n\n## Implementation Order\n- Fix each deviation exactly at the referenced node/edge.\n- Add or correct missing endpoints/connections.\n- Run VALIDATE ARCH again until no red deviation remains.\n\n## Acceptance Criteria\n- [ ] All red deviations are fixed.\n- [ ] Validation reports "No deviations found".`;
}
function exportDeviationBrief(){fileName='deviation-dev-brief.md';openModal('Deviation Development Brief',deviationBrief())}
function draftDeviationForNode(id){let d=nodeDeviation(id);if(!d){alert('No deviation on node '+id);return;}fileName='deviation-'+id+'.md';openModal('Deviation Brief: '+id,`# Development Brief: Deviation ${id}\n\n- Node: ${id}\n- Issue: ${d.message}\n\n## Required Fix\n- Update implementation and architecture data so expected and rendered architecture match for this node.`)}


function hasSessionUserChanges(){return (model.changes||[]).some(c=>c.origin==='user-edit')}
function currentDevBriefId(){return model.project?.activeDevBriefId||'default-brief'}
function pendingAutoImproveMatchesBrief(pending,briefId){
  if(!pending)return false;
  // Legacy proposals can have null/undefined devBriefId; treat only those as current brief to avoid duplicate prompts.
  let pendingBriefId=pending.devBriefId??briefId;
  return pendingBriefId===briefId;
}
function historyAutoImproveMatchesBrief(history,briefId){
  if(!Array.isArray(history))return false;
  return history.some(h=>h?.devBriefId===briefId);
}
function hasAutoImproveForBrief(){let briefId=currentDevBriefId(),ai=model.autoImprove||{};let pendingSameBrief=pendingAutoImproveMatchesBrief(ai.pending,briefId);let historySameBrief=historyAutoImproveMatchesBrief(ai.history,briefId);return {blocked:Boolean(pendingSameBrief||historySameBrief),briefId,pendingSameBrief,historySameBrief}}
function inferGoalStatement(){let p=model.project||{};if(p.goal)return p.goal;let constraints=(model.nodes||[]).flatMap(n=>n.detail?.constraints||[]).slice(0,2);return p.description||constraints.join(' ')||'Improve delivery toward architecture goals with low-to-medium effort and high impact.'}
function evaluateAutoImprove(){
  if(hasSessionUserChanges())return {allowed:false,reason:'Auto-improve is locked because this session already contains user-requested architecture changes.'};
  let briefGuard=hasAutoImproveForBrief();
  if(briefGuard.blocked){
    let detail=briefGuard.pendingSameBrief?'pending proposal already exists':'proposal already confirmed in history';
    return {allowed:false,reason:'Auto-improve can only be triggered once per dev brief. Blocked for devBriefId: '+briefGuard.briefId+' ('+detail+').'};
  }
  let nodes=(model.nodes||[]).filter(n=>!n._deleted),edges=(model.edges||[]),apis=nodes.flatMap(n=>n.detail?.apis||[]),deviationCount=Object.keys(model.deviations?.nodes||{}).length+Object.keys(model.deviations?.edges||{}).length;
  let risks=[];
  if(!apis.length)risks.push('Low observability of API contracts in architecture data');
  if(!model.health)risks.push('No recent runtime health signal present');
  if(deviationCount>0)risks.push('Known architecture deviations may conflict with new improvements');
  let suggestion={
    id:'ai-'+Math.random().toString(36).slice(2,9),
    createdAt:now(),
    title:'Architecture Guardrail Pipeline',
    summary:'Introduce a CI guardrail that runs architecture validation + flow extraction on each PR and fails on red deviations.',
    rationale:'Small-to-medium implementation effort with strong leverage: protects strategic architecture drift, improves maintainability, and keeps changes aligned with goals.',
    impact:'Expected impact: high alignment and reduced regression risk across future changes.',
    effort:'medium',
    goal:inferGoalStatement(),
    scope:['Add non-interactive validator command', 'Persist expectedArchitecture baseline', 'Publish deviation report artifact in CI'],
    riskAssessment:{level:deviationCount>0?'high':'medium',items:risks},
    mitigations:[
      'Start with warning mode for first rollout window',
      'Require explicit baseline update in same PR for intentional architecture changes',
      'Add ownership for false-positive triage and weekly review'
    ],
    dependencies:['Architecture JSON baseline in repository', 'CI runtime with Python 3'],
    successMetrics:['Deviation count trend decreases', 'PRs with unreviewed architecture drift reduced', 'Mean time to detect architecture regressions reduced']
  };
  return {allowed:true,suggestion};
}
function architectureSignature(){
  let nodes=(model.nodes||[]).filter(n=>!n._deleted).map(n=>n.id).sort();
  let edges=(model.edges||[]).map(e=>e.from+'->'+e.to).sort();
  let userChanges=(model.changes||[]).filter(c=>c.origin==='user-edit').length;
  return JSON.stringify({nodes,edges,userChanges});
}
function triggerAutoImprove(){
  let result=evaluateAutoImprove();
  if(!result.allowed){alert(result.reason);return}
  let ai=model.autoImprove=model.autoImprove||{history:[]};
  let briefId=currentDevBriefId();
  let suggestion=result.suggestion;
  suggestion.devBriefId=briefId;
  suggestion.status='proposed';
  suggestion.guard={signatureAtProposal:architectureSignature(),userChangeCountAtProposal:(model.changes||[]).filter(c=>c.origin==='user-edit').length};
  ai.pending=suggestion;
  change({type:'auto-improve-proposed',target:'strategy',origin:'system',after:suggestion,description:'Auto-improve proposal generated: '+suggestion.title});
  openModal('Auto-Improve Proposal',formatAutoImproveProposal(suggestion));
}
function confirmAutoImprove(){
  let ai=model.autoImprove||{}; if(!ai.pending){alert('No auto-improve proposal to confirm.');return}
  let pending=ai.pending;
  let nowSignature=architectureSignature();
  if(pending.guard&&pending.guard.signatureAtProposal!==nowSignature){
    alert('Confirmation blocked: architecture changed after proposal creation. Re-run AUTO-IMPROVE to avoid contradictions.');
    return;
  }
  if(hasSessionUserChanges()){
    alert('Confirmation blocked: user-edit changes exist in this session. Auto-improve must run on an unchanged architecture state.');
    return;
  }
  let confirmed={...pending,devBriefId:pending.devBriefId||currentDevBriefId(),status:'confirmed',confirmedAt:now()};
  ai.history=ai.history||[]; ai.history.push(confirmed); delete ai.pending;
  model.devBriefs=model.devBriefs||[];
  model.devBriefs.push({id:'brief-'+Math.random().toString(36).slice(2,8),createdAt:now(),source:'auto-improve',title:confirmed.title,content:formatAutoImproveDevBrief(confirmed)});
  change({type:'auto-improve-confirmed',target:'dev-brief',origin:'system',after:confirmed,description:'Auto-improve confirmed and converted to development brief'});
  openModal('Auto-Improve Dev Brief',formatAutoImproveDevBrief(confirmed));
}
function formatAutoImproveProposal(s){return `# Auto-Improve Proposal

## Title
${s.title}

## Strategic Goal Context
${s.goal}

## Why this is impactful
${s.rationale}

## Effort
${s.effort}

## Suggested Scope
${s.scope.map(x=>'- '+x).join('\n')}

## Risk Assessment
- Level: ${s.riskAssessment.level}
${(s.riskAssessment.items||[]).map(x=>'- '+x).join('\n')||'- No critical risks identified'}

## Mitigations
${s.mitigations.map(x=>'- '+x).join('\n')}

## Success Metrics
${s.successMetrics.map(x=>'- '+x).join('\n')}
`}
function formatAutoImproveDevBrief(s){return `# Development Brief: Auto-Improve

## Selected Improvement
- Title: ${s.title}
- Confirmed At: ${s.confirmedAt||now()}
- Dev Brief Context: ${s.devBriefId}

## Strategic Intent
${s.goal}

## Implementation Plan
${s.scope.map((x,i)=>`${i+1}. ${x}`).join('\n')}

## Risk & Contradiction Controls
${s.mitigations.map(x=>'- '+x).join('\n')}

## Required Architectural Consistency Checks
- Validate against expectedArchitecture baseline before merge.
- Evaluate every follow-up architecture change for contradiction, risk, and synergy against this improvement.
- Reject impulsive short-term-only changes without strategic fit rationale.
`}
function statusRank(s){return ({red:3,yellow:2,green:1,unknown:0})[s]||0}
function worstStatus(list){let w='unknown';(list||[]).forEach(x=>{let s=String(x?.status||'unknown').toLowerCase();if(statusRank(s)>statusRank(w))w=s});return w}
function nodeHealth(id){let h=model.health?.nodes?.[id]||{};let endpoints=Array.isArray(h.endpoints)?h.endpoints:[];let status=(h.status||worstStatus(endpoints)||'unknown').toLowerCase();return {status:['red','yellow','green','unknown'].includes(status)?status:'unknown',summary:h.summary||h.message||''}}
function apiHealth(nodeId,index){let ep=model.health?.nodes?.[nodeId]?.endpoints?.[index]||{};let status=String(ep.status||'unknown').toLowerCase();return {status:['red','yellow','green','unknown'].includes(status)?status:'unknown',summary:ep.summary||ep.error||ep.message||''}}
function edgeHealth(e){let key=e.from+'->'+e.to,h=model.health?.edges?.[key]||model.health?.edges?.[e.from+'|'+e.to]||{};let status=String(h.status||'unknown').toLowerCase();return {status:['red','yellow','green','unknown'].includes(status)?status:'unknown',summary:h.summary||''}}
function edgeColor(e){let eh=edgeHealth(e);if(eh.status==='red')return '#ff5c5ccc';if(eh.status==='yellow')return '#ffd35acc';if(eh.status==='green')return '#2dff7acc';let a=nodeHealth(e.from).status,b=nodeHealth(e.to).status,w=worstStatus([{status:a},{status:b}]);if(w==='red')return '#ff5c5ccc';if(w==='yellow')return '#ffd35acc';if(w==='green')return '#2dff7acc';return e.style==='api'?'#77a7ff99':'#c9a84c99'}
async function runHealthCheck(){let url=prompt('Health-check server URL',model.project?.healthCheckUrl||'');if(!url)return;model.project=model.project||{};model.project.healthCheckUrl=url;try{await callLiveApiHealthCheck(url,{timeoutMs:30000});alert('live API check complete');}catch(err){alert('live API check failed: '+err.message)}}
async function callLiveApiHealthCheck(serverUrl,options={}){let checks=[],flows=extractArchitectureFlows();flows.forEach((f,i)=>checks.push({nodeId:f.target,source:f.source,target:f.target,flowIndex:i,endpointIndex:i,method:f.method,path:f.path,description:f.description,critical:f.critical,expectedStatus:[200,201,202,204]}));(model.nodes||[]).forEach(n=>{(n.detail?.apis||[]).forEach((a,i)=>{let exists=checks.some(c=>c.nodeId===n.id&&c.method===(a.method||'GET')&&c.path===(a.path||''));if(!exists)checks.push({nodeId:n.id,endpointIndex:i,method:a.method||'GET',path:a.path||'',url:a.url||'',headers:a.headers||{},query:a.query||{},body:a.body??null,expectedStatus:a.expectedStatus||a.expected_status||[200,201,202,204],expectedResponse:a.expectedResponse||a.expected_response||null})})});let controller=new AbortController(),timer=setTimeout(()=>controller.abort(),options.timeoutMs||30000);let endpoint=serverUrl.replace(/\/$/,'')+'/probe-architecture';let res;try{res=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json',...(options.apiKey?{'Authorization':'Bearer '+options.apiKey}:{})},body:JSON.stringify({project:model.project||{},nodes:model.nodes||[],edges:model.edges||[],flows,checks}),signal:controller.signal});}finally{clearTimeout(timer)}if(!res.ok)throw new Error('HTTP '+res.status+' from '+endpoint);let report=await res.json();model.health=normalizeHealthReport(report);change({type:'probe',target:'architecture-health',before:null,after:model.health,description:'Live API health check: '+(model.health.summary?.status||'unknown')});return model.health}
function normalizeHealthReport(report){let out={timestamp:report.timestamp||now(),summary:report.summary||{},nodes:{},edges:report.edges||{}};if(report.nodes&&!Array.isArray(report.nodes)){Object.entries(report.nodes).forEach(([id,h])=>out.nodes[id]={status:String(h.status||'unknown').toLowerCase(),summary:h.summary||h.message||'',endpoints:h.endpoints||[]});return out}(report.results||[]).forEach(r=>{let id=r.nodeId||r.node_id;if(!id)return;let idx=Number(r.endpointIndex??r.endpoint_index??0);out.nodes[id]=out.nodes[id]||{status:'unknown',summary:'',endpoints:[]};out.nodes[id].endpoints[idx]={status:String(r.status||'unknown').toLowerCase(),summary:r.summary||r.error||r.message||'',httpStatus:r.httpStatus||r.http_status||null,latencyMs:r.latencyMs||r.latency_ms||null};});Object.entries(out.nodes).forEach(([id,h])=>{h.status=h.status==='unknown'?worstStatus(h.endpoints):h.status;h.summary=h.summary||((h.endpoints||[]).filter(Boolean).map(e=>e.summary).filter(Boolean)[0]||'')});return out}

function saveLocal(){localStorage.setItem('omni-architecture-model',JSON.stringify(model));alert('saved')}function loadLocal(){let raw=localStorage.getItem('omni-architecture-model');if(raw){model=JSON.parse(raw);render()}}function dl(name,text,type='text/plain'){let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click()}function downloadJSON(){dl('architecture.json',JSON.stringify(model,null,2),'application/json')}
function methodRank(m){return ({GET:1,POST:2,PUT:3,PATCH:4,DELETE:5})[String(m||'').toUpperCase()]||99}
function inferFlowDescription(e,a){return e.description||e.desc||e.label||a?.desc||a?.description||e.data||'Service-to-service API call'}
function isServiceNode(n){let t=String(n?.type||'').toLowerCase(),tags=(n?.detail?.tags||[]).map(x=>String(x).toLowerCase());return ['service','api','agent','workflow','domain','external','infra'].includes(t)||tags.some(x=>['service','api','backend','worker','runtime'].includes(x))}
function isStaticOrInternalFlow(e,a){let rel=String(e?.relation||'').toLowerCase(),protocol=String(e?.protocol||'').toLowerCase(),label=String(e?.label||'').toLowerCase(),path=String(a?.path||e?.path||'').toLowerCase(),txt=[rel,protocol,label,path,String(e?.data||'').toLowerCase()].join(' ');if(txt.includes('ollama'))return true;if(['file','static','filesystem'].includes(protocol))return true;if(rel.includes('file')||rel.includes('static'))return true;if(path.startsWith('file:')||path.includes('/static/')||path.includes('/assets/'))return true;return false}
function endpointMatchesEdge(a,e){if(!a)return false;let consumers=Array.isArray(a.consumers)?a.consumers.map(String):[];if(consumers.includes(e.from)||consumers.includes(e.to))return true;if(e.path&&a.path===e.path)return true;if(e.method&&String(a.method||'').toUpperCase()===String(e.method).toUpperCase()&&(e.path?a.path===e.path:true))return true;return false}
function pickFlowEndpoint(source,target,e){let apis=(target.detail?.apis||[]).filter(a=>endpointMatchesEdge(a,e));if(!apis.length)apis=(target.detail?.apis||[]).filter(a=>['POST','PUT','PATCH','GET','DELETE'].includes(String(a.method||'').toUpperCase()));apis.sort((a,b)=>(String(a.path||'')+methodRank(a.method)).localeCompare(String(b.path||'')+methodRank(b.method)));return apis[0]||null}
function extractArchitectureFlows(){let nodesById=Object.fromEntries((model.nodes||[]).map(n=>[n.id,n])),flows=[];(model.edges||[]).forEach(e=>{let source=nodesById[e.from],target=nodesById[e.to];if(!source||!target||source._deleted||target._deleted)return;let rel=String(e.relation||e.style||'').toLowerCase(),protocol=String(e.protocol||'').toLowerCase();let looksCall=rel.includes('api')||rel.includes('event')||rel.includes('data')||['http','https','queue','event','grpc'].includes(protocol)||e.method||e.path;if(!looksCall)return;if(!isServiceNode(source)||!isServiceNode(target))return;let api=pickFlowEndpoint(source,target,e);if(isStaticOrInternalFlow(e,api))return;let method=String(e.method||api?.method||'GET').toUpperCase();let path=e.path||api?.path||api?.url||'';if(!path)return;flows.push({source:e.from,target:e.to,method,path,description:inferFlowDescription(e,api),critical:Boolean(e.critical??api?.critical??(e.style==='primary'||rel.includes('api-call')))});});let seen=new Set();return flows.filter(f=>{let k=[f.source,f.target,f.method,f.path].join('|');if(seen.has(k))return false;seen.add(k);return true}).sort((a,b)=>a.source.localeCompare(b.source)||a.target.localeCompare(b.target)||a.path.localeCompare(b.path)||methodRank(a.method)-methodRank(b.method))}
function formatArchitectureFlows(){let flows=extractArchitectureFlows();if(!flows.length)return 'No service-to-service API flows documented.';return flows.map(f=>`### Flow: ${f.source} → ${f.target}\n- Source: ${f.source}\n- Target: ${f.target}\n- Method: ${f.method}\n- Path: ${f.path}\n- Description: ${String(f.description||'').replaceAll('\\n',' ')}\n- Critical: ${f.critical?'true':'false'}`).join('\\n\\n')}
function devBrief(){let cs=model.changes||[];if(!cs.length)return '# Development Brief: No Changes\n\nNo architecture edits have been recorded.';return `# Development Brief: Architecture Change Request\n\n## 1. Brief Metadata\n- Project: ${model.project?.name||'Unknown'}\n- Generated: ${now()}\n- Source: architecture editor change log\n- Change Count: ${cs.length}\n\n## 2. Change Summary\n| Type | Target | Component | Summary |\n|---|---|---|---|\n${cs.map(c=>`| ${c.type} | ${c.target} | ${c.nodeId||''} | ${String(c.description||'').replaceAll('|','/')} |`).join('\n')}\n\n## 3. Surgical Edit Instructions\n${cs.map((c,i)=>`### Change ${i+1}: ${c.description||c.target}\n- Type: ${c.type}\n- Target: ${c.target}\n- Component: ${c.nodeId||'n/a'}\n- Before:\n\`\`\`json\n${JSON.stringify(c.before??null,null,2)}\n\`\`\`\n- After:\n\`\`\`json\n${JSON.stringify(c.after??null,null,2)}\n\`\`\`\n- Required implementation: update the affected architecture object exactly as shown above.`).join('\n\n')}\n\n## 4. Acceptance Criteria\n- [ ] All before/after changes are implemented exactly.\n- [ ] Modified endpoints, flows, and edges are covered by tests or documented manual checks.\n\n## 5. Non-Goals\n- Do not refactor unrelated components.\n`}
function snapshot(){let nodes=[...(model.nodes||[])].sort((a,b)=>a.id.localeCompare(b.id)),ed=[...(model.edges||[])].sort((a,b)=>(a.from+a.to).localeCompare(b.from+b.to)),apis=[];nodes.forEach(n=>(n.detail?.apis||[]).forEach(a=>apis.push({node:n.id,...a})));apis.sort((a,b)=>(a.path+a.method).localeCompare(b.path+b.method));return `# Architecture Snapshot: ${model.project?.name||'Project'}\n\n## 0. Header Block\n- Project: ${model.project?.name||'Unknown'}\n- Domain: ${model.project?.domain||'unknown'}\n- Repo: ${model.project?.repo||''}\n- Generated: ${now()}\n- Nodes: ${nodes.length}\n- Edges: ${ed.length}\n- Endpoints: ${apis.length}\n\n## Table of Contents\n1. Introduction & Goals\n2. Constraints\n3. Context & Scope\n4. Solution Strategy\n5. Building Block View\n6. Runtime View - User Flows\n7. API Reference\n8. Module Catalogue\n9. Glossary\n10. Architecture Flows\n\n## 1. Introduction & Goals\n${model.project?.description||'No description provided.'}\n\n## 2. Constraints\n${nodes.flatMap(n=>n.detail?.constraints||[]).map(x=>'- '+x).join('\n')||'- Unknown - search required'}\n\n## 3. Context & Scope\n\`\`\`mermaid\nflowchart LR\n${ed.map(e=>`  ${id(e.from)}[${e.from}] --> ${id(e.to)}[${e.to}]`).join('\n')}\n\`\`\`\n\n## 4. Solution Strategy\n- Architecture is represented as editable nodes and edges.\n- Changes are captured as before/after deltas.\n\n## 5. Building Block View\n\`\`\`mermaid\nflowchart TD\n${nodes.map(n=>`  ${id(n.id)}[${n.label||n.id}]`).join('\n')}\n${ed.map(e=>`  ${id(e.from)} --> ${id(e.to)}`).join('\n')}\n\`\`\`\n\n## 6. Runtime View - User Flows\n${nodes.map(n=>`### ${n.label||n.id}\n${(n.detail?.flow||[]).map((s,i)=>`${i+1}. ${s}`).join('\n')||'No flow documented.'}`).join('\n\n')}\n\n## 7. API Reference\n### 7.1 Endpoint Index\n| Method | Path | Module | Description |\n|---|---|---|---|\n${apis.map(a=>`| ${a.method||''} | ${a.path||''} | ${a.node} | ${String(a.desc||'').replaceAll('|','/')} |`).join('\n')||'| | | | |'}\n\n### 7.2 Endpoint Details\n${apis.map(a=>`#### ${a.method} ${a.path}\n- Module: ${a.node}\n- Description: ${a.desc||''}\n- Parameters:\n${(a.params||[]).map(p=>'  - '+p).join('\n')||'  - none documented'}`).join('\n\n')||'No endpoints documented.'}\n\n## 8. Module Catalogue\n| Module | Type | Responsibility | Tags | Notes |\n|---|---|---|---|---|\n${nodes.map(n=>`| ${n.id} | ${n.type||''} | ${String(n.detail?.subtitle||n.sub||'').replaceAll('|','/')} | ${(n.detail?.tags||[]).join(', ')} | ${String(n.detail?.notes||'').replaceAll('|','/')} |`).join('\n')}\n\n## 9. Glossary\n| Term | Meaning |\n|---|---|\n| Node | Architecture component, module, service, view, agent, data object, or external system. |\n| Edge | Relationship, flow, API call, dependency, event, data movement, or ownership link. |\n\n## 10. Architecture Flows\n${formatArchitectureFlows()}\n`}function id(s){return String(s).replace(/[^a-zA-Z0-9_]/g,'_')}function showBrief(){fileName='development-brief.md';openModal('Development Brief',devBrief())}function showSnapshot(){fileName='architecture-snapshot.md';openModal('Architecture Snapshot',snapshot())}function openModal(t,x){dom.modalTitle.textContent=t;dom.modalText.value=x;dom.modal.classList.add('open')}function closeModal(){dom.modal.classList.remove('open')}function copyModal(){navigator.clipboard.writeText(dom.modalText.value)}function downloadModal(){dl(fileName,dom.modalText.value,'text/markdown')}render();
</script></body></html>'''


def render_html(model: dict[str, Any]) -> str:
    payload = json.dumps(model, ensure_ascii=False, indent=2).replace("</", "<\\/")
    title = escape(str(model.get("project", {}).get("name", "Architecture Editor")))
    return HTML.replace("__TITLE__", title).replace("__MODEL_JSON__", payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate editable architecture HTML.")
    parser.add_argument("--input", help="Path to architecture JSON")
    parser.add_argument("--output", required=True, help="Output HTML path")
    args = parser.parse_args()
    Path(args.output).write_text(render_html(load_model(args.input)), encoding="utf-8")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
