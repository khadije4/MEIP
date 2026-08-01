import type { Point } from '../types/economic'

export function base100(points:Point[],start:number,end:number):Point[]{
  const selected=points.filter(p=>p.year>=start&&p.year<=end);const base=selected.find(p=>p.value!=null&&Number.isFinite(p.value))?.value
  return selected.map(p=>({...p,value:p.value==null||base==null||base===0?null:p.value/base*100}))
}
export function annualGrowth(points:Point[],start:number,end:number):Point[]{
  const map=new Map(points.map(p=>[p.year,p.value]));return points.filter(p=>p.year>=start&&p.year<=end).map(p=>{const previous=map.get(p.year-1);return {...p,value:p.value==null||previous==null||previous===0?null:(p.value-previous)/Math.abs(previous)*100}})
}
export function summarizeComparison(points:Point[],start:number,end:number){
  const selected=points.filter(p=>p.year>=start&&p.year<=end&&p.value!=null) as Array<Point&{value:number}>;const growth=annualGrowth(points,start,end).flatMap(p=>p.value==null?[]:[p.value]);
  if(!selected.length)return {latest:null,min:null,max:null,averageGrowth:null,volatility:null,totalChange:null}
  const latest=selected.at(-1)!;const min=selected.reduce((a,b)=>a.value<=b.value?a:b);const max=selected.reduce((a,b)=>a.value>=b.value?a:b);const avg=growth.length?growth.reduce((a,b)=>a+b,0)/growth.length:null;const volatility=growth.length>1?Math.sqrt(growth.reduce((sum,v)=>sum+(v-(avg??0))**2,0)/(growth.length-1)):null;const first=selected[0].value
  return {latest,min,max,averageGrowth:avg,volatility,totalChange:first===0?null:(latest.value-first)/Math.abs(first)*100}
}
export function hasCalendarGaps(points:Point[],start:number,end:number){const years=new Set(points.filter(p=>p.value!=null).map(p=>p.year));return Array.from({length:end-start+1},(_,i)=>start+i).some(y=>!years.has(y))}
