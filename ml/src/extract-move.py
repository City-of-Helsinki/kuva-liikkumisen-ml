'''
Extract Move! scores from PDF

This script extracts tables from the Move! reports sent to schools as PDF files
Työkalu joka purkaa kouluille lähetettyjen Move!-raporttien PDF:istä taulukoita

The School name is replaced with KouluID.


Requires:

  ./move_koulu.tsv - Move! school name to internal name mapping
  ../input/SALAINEN_Koulu_KouluID.xlsx - School name -> KouluID mapping
  
  PDF folder:
  ../../m-suojaamaton/movetulokset/

Produces:

  ../data/move-osuudet_YYYY.tsv - 20 metrin viivajuoksun osuudet luokittain
  ../data/move-summary_YYYY.tsv - Per-school summary score rows


Known problems:
        * Only "t" group: Poikkilaakson ala-asteen koulu
        * No KouluID: Maunulan yhteiskoulu

'''


# In[imports]

import os
import pandas as pd
import re
import subprocess
from collections import defaultdict


# In[funcs]



def digest_move_summary(move_lines):

    mode = 'koulu' # koulu - luokka - ryhma - laji
    school_name = ''
    luokka_list = []
    laji_id = 'x'
    scores = defaultdict(list)
    sc_units = dict()

    for txt in move_lines:
        if (mode == 'koulu'):
            r = re.search(r"^Tulosten yhteenveto: (.*)$",txt)
            if (r):
                school_name = r.group(1)
                school_name = re.sub(r" - .*$","",school_name)
                mode = 'luokka'

        if (mode == 'luokka'):
            r = re.search(r"\s*([0-9]+)\. luokka.*$",txt)
            if (r):
                luokka_list.append(r.group(1))

            r = re.search(r"\s*OSIO",txt)
            if (r):
                mode = 'ryhma'

        if (mode == 'ryhma' or mode == 'laji'):
            r = re.search(r"\s*(.*) \((.*)\)",txt)
            if r and not (('median' in txt or ('medel' in txt))):
                mode = 'laji'
                laji_id = r.group(1)
                sc_units[laji_id] = r.group(2)

        if (mode == 'laji'):
            r = re.search(r"\s*(\d\S*)\s*$",txt)
            if r and len(scores[laji_id]) < (len(luokka_list)*2):
                scores[laji_id].append(r.group(1))
                
    scorefields = []
    for k in scores.keys():
        for i,v in enumerate(scores[k]):
            scorefields.append((school_name,
                  k,
                  sc_units[k],
                  luokka_list[int(i/2)],
                              'p' if i%2 else 't',
                              v))
    df = pd.DataFrame(scorefields,
                      columns=['koulun_nimi','osio','yks','luokka',
                               'sukupuoli','move_tulos'])
    
    return df




def extract_text_cells(tab_txt):

    viiva_rows = tab_txt.split('\n')
    textcells = []

    for rowid,row_in in enumerate(viiva_rows):
        col = 0
        m = True
        while (m):
            m = re.search("^(\s*)(\S+)(.*)$",row_in[col:])
            if m:
                col += len(m.group(1)) # whitespace
                mtxt = m.group(2)
                if ("%" in mtxt):
                    mtxt = mtxt[0:(mtxt.index('%')+1)]
                textcells.append((rowid,col,mtxt))
                col += len(mtxt)

    return textcells


# In[funcs2]


xxx_problem_pool = []


# In[main]

def main():
    '''
    This loop extracts a couple of statistics from the Move! PDF reports

    Returns
    -------
    None.

    '''

        
    
    kouluid_map = pd.DataFrame(pd.read_excel("../input/SALAINEN_Koulu_KouluID.xlsx"),
                               columns=['Koulu_ID','Koulu']).\
        set_index('Koulu').Koulu_ID
    
    move_schools = pd.read_csv("move_koulu.tsv",sep="\t").\
        set_index("Move_koulu").Koulu
    
    move_path = "../../m-suojaamaton/movetulokset/"
    file_pool = [os.path.join(move_path,x) for x in os.listdir(move_path) if x.endswith(".pdf")]
    
        
    
    # main loop
    
    global xxx_problem_pool
    global yearid
    
    
    for file_name in file_pool:    
            
        # summary page results
        
        result = subprocess.run(["pdftotext -f 7 -l 7 "+file_name+" -"], shell=True, capture_output=True, text=True)
        move_summarypage = result.stdout
        summary_df = digest_move_summary(move_summarypage.split("\n"))
        #print(summary_df)
            
         
        # Saving summary page
        
        # Extract school metadata
        
        m = re.search(r".*_move(20\d\d)\.",file_name)
        yearid = 1984
        if m:
            yearid = int(m.group(1))
        
        schoolname = summary_df.iloc[0].koulun_nimi
        schoolid=-1
        
        if (schoolname in move_schools.index):
            schoolname = move_schools.loc[schoolname]
        
        schoolname_lookup_pool = [schoolname,schoolname.replace('koulu','peruskoulu')]
        for n in schoolname_lookup_pool:
            if n in kouluid_map.index:
                schoolid = kouluid_map.loc[n]
        
        if (schoolid<0):
            xxx_problem_pool.append("%s not mapped" % schoolname)
            
        if schoolid>=0: # DEBUG  and schoolname == "Poikkilaakson ala-asteen koulu":
        
            csvbasename = "move_%04d_koulu_%d" % (yearid,schoolid)
            print("Base ID %s" % csvbasename)
            
            summary_df['Koulu_ID'] = schoolid
            summary_df['vuosi'] = yearid
            summary_df = pd.DataFrame(summary_df,columns=list(summary_df.columns[-2:]) + list(summary_df.columns[0:-2]))
            csvname = "../data/%s_summary.tsv"%csvbasename
            summary_df.to_csv(csvname,sep='\t',index=False)
            
            print("Written %s"%csvname)
            
            if True:
            
                # Osuus report pages
                
                result = subprocess.run(["pdftotext -f 8 -fixed 4 "+file_name+" -"], shell=True, capture_output=True, text=True)
                move_details = result.stdout
                osuus_pgs = [pg for pg in move_details.split('\f') if ', osuudet ' in pg]
                
                for osuus_txt in osuus_pgs:
                    luokka = "-"
                    m = re.search(r"(\d)\.?\s+luokka",osuus_txt)
                    if m:
                        luokka = m.group(1)
                
                    laji = "-"
                    m = re.search(r"\s*(\S.*\S), osuudet",osuus_txt)
                    if m:
                        laji = m.group(1)
                
                    #print(luokka, laji)
                    
                    
                    if '20 m viivajuoksu' == laji:
                        cells = extract_text_cells(osuus_txt)
                        colvals = [(c,t) for (r,c,t) in cells if t.endswith('%') and r>2]
                        barchart_values = pd.DataFrame(colvals,columns=['xpos','value']).sort_values('xpos').reset_index(drop=True)
                        #print(barchart_values)
                        
                        if len(barchart_values.value)==12:
                            barchart_values.value = barchart_values.value.str.replace("%","")
                        
                            barnames = [("osuus_%s"%x) for x in ['ref_A','A','ref_B','B','ref_C','C']]
                            osuus1_df = pd.DataFrame([[schoolname,laji,luokka,'t']+list(barchart_values.value[0:6])])
                            osuus1_df.columns = ['koulun_nimi','laji','luokka','sukupuoli']+barnames
                            osuus1_df
                    
                            osuus2_df = pd.DataFrame([[schoolname,laji,luokka,'p']+list(barchart_values.value[6:12])])
                            osuus2_df.columns = ['koulun_nimi','laji','luokka','sukupuoli']+barnames
                            osuus2_df
                    
                            osuus_df = pd.concat([osuus1_df,osuus2_df])
                            osuus_df['Koulu_ID'] = schoolid
                            osuus_df['vuosi'] = yearid
                            osuus_df = pd.DataFrame(osuus_df,columns=['Koulu_ID','vuosi']+list(osuus1_df.columns)).reset_index(drop=True)
                            #print(osuus_df)
                            
                            csvname = "../data/%s_%slk_osuudet.tsv"%(csvbasename,luokka)
                            osuus_df.to_csv(csvname,sep='\t',index=False)
                            
                            print("Written %s"%csvname)
                            
                        else:
                            xxx_problem_pool.append("Missing 12 bars on details page %s %s %s "%(schoolname,laji,luokka))
                        



# In[compose]



def compose_suojattu(suffix,data_path="../data"):
    part_dfs=[]
    for f in [os.path.join(data_path,x) for x in os.listdir(data_path) if x.endswith("_%s.tsv"%suffix)]:
        part_dfs.append(pd.read_csv(f,sep="\t"))
    part_df = pd.concat(part_dfs).reset_index(drop=True).drop(columns=['koulun_nimi'])
    tsvname = "../data/move-%s_%s.tsv"%(suffix,yearid)
    part_df.to_csv(tsvname,sep="\t",index=False)
    print(tsvname, part_df.shape)
    
    


# In[run]

xxx_problem_pool=[]
main()
print(xxx_problem_pool)

# In[run]

compose_suojattu("osuudet")
compose_suojattu("summary")

