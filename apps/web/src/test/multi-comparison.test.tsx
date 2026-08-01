import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LanguageProvider } from '../contexts/LanguageContext'
import { MultiComparePage } from '../pages/MultiComparePage'
import { api } from '../services/api'
import { annualGrowth, base100 } from '../utils/comparison'
import { MemoryRouter } from 'react-router-dom'

const names=[['fishing','Pêche'],['extractive_activities','Activités extractives'],['commerce','Commerce'],['construction_public_works','BTP'],['manufacturing','Industrie'],['transport','Transport'],['primary_sector','Secteur primaire']]
const indicators=names.map(([code,name],id)=>({id,code,name_fr:name,name_ar:name,category:'sector',hierarchy_level:1,unit:'Millions de MRU',source_side:'activity',is_aggregate:false,is_alias:false}))
const points=[{year:2020,value:10},{year:2021,value:null},{year:2022,value:20},{year:2023,value:30},{year:2024,value:40}]
function setup(){vi.spyOn(api,'get').mockImplementation(async path=>({data:String(path)==='/api/indicators'?indicators:{points}}) as never)}
function renderPage(path='/explore?tab=compare'){return render(<LanguageProvider><MemoryRouter initialEntries={[path]}><MultiComparePage/></MemoryRouter></LanguageProvider>)}
async function add(name:string){const user=userEvent.setup();const input=screen.getByPlaceholderText('Rechercher…');await user.type(input,name);await user.click(await screen.findByRole('button',{name}));}

describe('multi-indicator comparison',()=>{beforeEach(setup);afterEach(()=>vi.restoreAllMocks())
 it('selects three indicators and removes one without duplicates',async()=>{renderPage();await screen.findByText('Comparer de 2 à 6 indicateurs');await add('Commerce');expect(screen.getByRole('button',{name:'Retirer Commerce'})).toBeInTheDocument();await userEvent.click(screen.getByRole('button',{name:'Retirer Commerce'}));expect(screen.queryByRole('button',{name:'Retirer Commerce'})).not.toBeInTheDocument()})
 it('supports six, switches to small multiples, and prevents a seventh',async()=>{renderPage();await screen.findByText('Comparer de 2 à 6 indicateurs');for(const name of ['Commerce','BTP','Industrie','Transport'])await add(name);expect(await screen.findByTestId('small-multiples')).toBeInTheDocument();expect(screen.getByPlaceholderText('Maximum de 6 atteint')).toBeDisabled();expect(screen.getAllByRole('button',{name:/Retirer/})).toHaveLength(6)})
 it('renders missing values and exports synchronized CSV',async()=>{const create=vi.fn(()=> 'blob:test');Object.defineProperty(URL,'createObjectURL',{value:create,configurable:true});Object.defineProperty(URL,'revokeObjectURL',{value:vi.fn(),configurable:true});vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(()=>{});renderPage();await screen.findByText('Comparer de 2 à 6 indicateurs');expect(await screen.findAllByTitle('Valeur non disponible')).not.toHaveLength(0);await userEvent.click(screen.getByRole('button',{name:'Télécharger CSV'}));expect(create).toHaveBeenCalled()})
 it('uses cached series calls for the selected indicators',async()=>{renderPage();await waitFor(()=>expect(vi.mocked(api.get).mock.calls.filter(([path])=>String(path).includes('/series'))).toHaveLength(2))})
 it('restores comparison selection from a direct URL',async()=>{renderPage('/explore?tab=compare&indicators=commerce,transport,manufacturing');expect(await screen.findByRole('button',{name:'Retirer Commerce'})).toBeInTheDocument();expect(screen.getByRole('button',{name:'Retirer Transport'})).toBeInTheDocument();expect(screen.getByRole('button',{name:'Retirer Industrie'})).toBeInTheDocument()})
})

describe('comparison calculations',()=>{
 it('calculates base 100 from the first valid selected value',()=>{expect(base100(points,2020,2024).map(p=>p.value)).toEqual([100,null,200,300,400])})
 it('calculates annual growth only for consecutive calendar years',()=>{const values=annualGrowth(points,2020,2024).map(p=>p.value);expect(values.slice(0,4)).toEqual([null,null,null,50]);expect(values[4]).toBeCloseTo(100/3)})
})
