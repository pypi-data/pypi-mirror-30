#!/usr/bin/env python3
import os
import sys
import subprocess
from bs4 import BeautifulSoup as BS
import urllib.request
import backoff
from lxml import etree as ET
import pandas as pd
import tqdm
import urllib
import numpy as np
import argparse
import re
from Bio import Entrez
import mygene
import time
import argparse
import csv
import backoff
import mimetypes
import importlib
import nltk
import nltk.corpus
import numpy as np
from PIL import Image
from os import path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

from gooey import Gooey, GooeyParser



running = True
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)

@Gooey(advanced=True,
    optional_cols=2,
    program_name="Gene Cloud",
    tabbed_groups=True,
    dump_build_config=True,
    show_success_modal=False,
    default_size=(1024, 768))

def window():
    parser = GooeyParser(description="An enhancer for PaperBlast")
    subs = parser.add_subparsers(help='commands', dest='command')
    parser_one = subs.add_parser('Pre-Woody', prog="PaperBlast")
    parser_one.add_argument('genes',default="id1\nid2", widget='Textarea',help="Uniprot IDs of your genes of interest. Separate by new lines",
                        metavar='Uniprot IDs',gooey_options={
                            'height': 10000})
    parser_one.add_argument("output",action="store",default="output.txt",widget='TextField',
                        metavar='Output File',help="Name of the output file")
    parser_two = subs.add_parser('Run-Woody', prog="Enhancer")
    parser_two.add_argument('pubmed',metavar='Pubmed IDs files',action='store',widget='FileChooser',help="Output file of Woody 1")
    parser_two.add_argument('basename', default="basename", widget="TextField",help="basename of the output files.",metavar='Basename')
    parser_two.add_argument('--terms', default="regex1\nregex2", widget="Textarea",help="Regex terms that the abstracts must have",
                        metavar='Terms',gooey_options={
                            'height': 10000})
    listimg = os.listdir(os.path.join(os.path.dirname(__file__), './pics'))
    parser_two.add_argument('--img',
                        metavar="Wordcloud Image",
                        help = "Choose one",
                        nargs="+",
                        default=['square'],
                        choices=sorted(listimg),
                        widget='Listbox',
                        gooey_options={
                            'height': 1000,
                            'heading_color': 'blue',
                            'text_color': 'red',
                        }
                        )
    parser_two.add_argument('--stopwords', default="word1\nword2",widget='Textarea',help="Stopword to clean your results",
                        metavar='Stopwords')
    parser_two.add_argument('--pubtator', default="", widget="TextField",help="output file name,  if empty not run Pubtator",metavar='Pubtator results')
    parser_two.add_argument('--project', default="", widget='TextField',help="Tagtog project name",metavar="Project name")
    parser_two.add_argument('--username', default="", widget='TextField',help="Tagtog username",
                        metavar='Username')
    parser_two.add_argument('--password', default="", widget='PasswordField',help="Tagtog password",
                        metavar='Password')
    args = parser.parse_args()
    return args

#PaperBlast

@backoff.on_exception(backoff.expo,urllib.error.URLError,max_value=32)
def get_text(gene):
    try:
        print("Searching gene in paperblast!")
        primarylist = []
        url = 'http://papers.genomics.lbl.gov/cgi-bin/litSearch.cgi?query=' + gene
        response = urllib.request.urlopen(url)
        data = response.read()      # a `bytes` object
        text = data.decode('utf-8')
        soup = BS(data,"lxml")
        for a in soup.findAll('a',href=True):
            if re.findall('pmc|pubmed', a['href']):
                primarylist.append(a['href'])
        return primarylist
    except:
        return False

def get_list(primarylist):
    listpmc = []
    listpubmed = []
    for x in primarylist:
        pmc = [s.rstrip() for s in x.split("/") if "PMC" in s]
        if len(pmc) != 0:
            listpmc.append(pmc[0])
        else:
            if "pubmed" in x:
                listpubmed.append(x.split("pubmed/")[-1].rstrip())
    listpmc = list(filter(None,listpmc))
    listpubmed = list(filter(None,listpubmed))
    listpmc = list(set(listpmc))
    listpubmed = list(set(listpubmed))
    listpmc = ",".join(listpmc).split(",")
    pmc = convert_pmc(listpmc)
    listpubmed = ",".join(listpubmed).split(",")
    pmids = pmc + listpubmed
    pmids = list(set(pmids))
    pmids = list(filter(None,pmids))
    print("Found",len(pmids),"associated with your gene in paperblast!")
    return ",".join(pmids)

@backoff.on_exception(backoff.expo,urllib.error.URLError,max_value=2)
def convert_pmc(pmc):
    print("Converting PMC ids to PMID!")
    pmclist = []
    for x in pmc:
        try:
            url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=genomepaper&email=anonymus@gmail.com&ids=" + x
            response = urllib.request.urlopen(url)
            data = response.read() 
            soup = BS(data,"lxml")
            for a in soup.findAll('record',pmid=True):
                pmclist.append(a['pmid'])
        except:
            pass
    print("Converting PMC ids to PMID: Done!")
    return pmclist

# Enhancer

def filter_abstact(pmids,gene,terms):
    print("Filtering abstract to find your terms associated with: ",gene)
    Entrez.email = 'anonymus@gmail.com'
    handle = Entrez.efetch(db="pubmed", id=','.join(map(str, pmids.split(","))),rettype="xml", retmode="text")
    records = Entrez.read(handle)
    larticle = []
    ids = []
    for pubmed_article in records['PubmedArticle']:           
        try:
            id = pubmed_article['MedlineCitation']['PMID'].rstrip()
            abstracts = pubmed_article['MedlineCitation']['Article']['Abstract']['AbstractText'][0]
        except:
            try:
                print(pubmed_article['MedlineCitation']['PMID'].rstrip(),"abstract not found!")
            except:
                print("abstract not found!")
            continue
        try: 
            title = pubmed_article['MedlineCitation']['Article']['ArticleTitle']
            journal = pubmed_article['MedlineCitation']['Article']['Journal']['Title']
        except:
            title = "-"
            journal =  "-"
        if len(terms) >0:
            for x in terms:
                if re.search(x, abstracts, re.IGNORECASE) is not None:                    
                    article = [gene,id,journal,title,abstracts,x]
                    larticle.append(article)
                    ids.append(id)
        else:  
            article = [gene,id,journal,title,abstracts]
            larticle.append(article)
            ids.append(id)                    
    if len(ids) == 0:
        print("For gene: ",gene,". No papers founds associated with your terms!")
        return larticle,ids
    na = str(len(ids))
    ids = list(set(ids))
    ids = list(filter(None,ids))
    ids = ",".join(ids)
    print(na, "abstract have your terms!")
    print("Filtering abstract to find your terms: Done!")
    return larticle,ids

def get_opener(filename):
    """
    Automatically detect compression and return the file opening function.
    """
    type_, encoding = mimetypes.guess_type(filename)
    if encoding is None:
        opener = open
    else:
        module = encoding_to_module[encoding]
        opener = importlib.import_module(module).open
    return opener

def extract_annotations(xml_path, tsv_path,gene,bool):
    """
    Extract the annotations from pubtator xml formatted file
    Outputs a TSV file with the following header terms:
    Document - the corresponding pubmed id
    Type - the type of term (i.e. Chemical, Disease, Gene etc.)
    ID - the appropiate MESH or NCBI ID if known
    Offset - the character position where the term starts
    End - the character position where the term ends
    Keywords arguments:
    xml_path -- The path to the xml data file
    tsv_path -- the path to output the formatted data
    """
    xml_opener = get_opener(xml_path)
    csv_opener = get_opener(tsv_path)
    genelist = []
    print("Creating PubTator for:", gene)
    with xml_opener(xml_path, "rb") as xml_file, csv_opener(tsv_path, "wt") as tsv_file:
        fieldnames = ['gene','pubmed_id', 'type', 'identifier']
        writer = csv.DictWriter(tsv_file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        tag_generator = ET.iterparse(xml_file, tag="document")
        for event, document in tqdm.tqdm(tag_generator):
            pubmed_id = document[0].text
            # cycle through all the annotation tags contained within document tag
            for annotation in document.iter('annotation'):
                # not all annotations will contain an ID
                if len(annotation) <= 3:
                    continue
                for infon in annotation.iter('infon'):
                    if infon.attrib["key"] == "type":
                        ant_type = infon.text
                    else:
                        ant_id = infon.text
                row = {'gene':gene,'pubmed_id': pubmed_id, 'type': ant_type, 'identifier': ant_id}
                if row["type"] == "Gene":
                    genelist.append(row["identifier"])
                writer.writerow(row)
            # prevent memory overload
            document.clear()
            if bool:
                continue
    df = pd.read_csv(tsv_path,sep="\t",header=0,usecols=['gene','pubmed_id', 'type', 'identifier'])
    df = df.apply(convert)    
    return list(set(genelist)),df


def get_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


@backoff.on_exception(backoff.expo,urllib.error.URLError,max_value=22)
def get_pubtator(pmids,gene):
    count = 0
    if len(pmids.split(",")) > 190:
        chunks = get_chunks(pmids.split(","), 100)
        for chunk in chunks:
            url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept/" + ",".join(chunk) + "/BioC/"
            response = urllib.request.urlopen(url)
            data = response.read()
            text = data.decode('utf-8') 
            oname = "PubTator-temp.xml"
            tsvoname = "PubTator-temp.tsv"
            fo = open(oname,"a")
            fo.write(text)
            if count == 0:
                count+=1
                id_list,df = extract_annotations(oname, tsvoname,gene,False)
                os.remove(oname)
                os.remove(tsvoname)
                fo.close()    
            else:
                try:
                    id_listc,dfc = extract_annotations(oname, tsvoname,gene,False)
                    id_list += id_listc
                    df = pd.concat([df, dfc])
                    os.remove(oname)
                    os.remove(tsvoname)
                    fo.close()
                except:
                    os.remove(oname)
                    os.remove(tsvoname)
                    fo.close()
    elif len(pmids.split(",")) == 1:
        return [],[]
    else:
        url = "https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/BioConcept/" + pmids + "/BioC/"
        response = urllib.request.urlopen(url)
        data = response.read()
        text = data.decode('utf-8') 
        oname = "PubTator-temp.xml"
        tsvoname = "PubTator-temp.tsv"
        fo = open(oname,"a")
        fo.write(text)
        try:
            id_list,df = extract_annotations(oname, tsvoname,gene,False)
        except:
            os.remove(oname)
            os.remove(tsvoname) 
            fo.close()
            return [],[]
        time.sleep(1)
        os.remove(oname)
        os.remove(tsvoname) 
        fo.close()
    print("Creating PubTator: Done!")
    return id_list,df

def convert(x):
    try:
        return x.astype(int)
    except:
        return x   

def gene_info(id_list,df):
    print("Fetching gene information from PubTator Tags!")    
    id_list = ",".join(id_list).replace(";",",").split(",")
    id_list = list(set(id_list))
    mg = mygene.MyGeneInfo()
    gene_info_list = []
    for gene in id_list:
        try:
            info = mg.getgene(int(gene))
            genes = [str(info['entrezgene']),info['symbol'],info['name'],info['taxid']]
            gene_info_list.append(genes)
        except:
            genes = [str(gene),"-","-","-"]
            gene_info_list.append(genes)
    dfi = pd.DataFrame(gene_info_list)
    dfi.columns = "identifier","symbol","name","taxid"
    df2 = pd.merge(df,dfi,on="identifier",how="left")
    df2.fillna('-', inplace=True)
    df2 = df2.apply(convert)
    print("Fetching gene information from PubTator Tags: Done!")    
    return df2

def grey_color_func(word, font_size, position, orientation, random_state=None,
                    **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def runcml(cml):
    process = subprocess.Popen(cml.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
    stdout, stderr = process.communicate()

def get_tagtog(pmids,project,username,password):
    print("Uploading articles to TagTog!")
    pmids = list(set(pmids))
    count = len(pmids)
    flag = True
    for x in pmids:
        try:
            cml = "tagtog upload --idType PMID --project " + project + " --user " + username + " --password " + password + " " + x
            runcml(cml)
            count -= 1
            print("There are",count,"left to be uploded")
        except:
            flag = False
            count -= 1
            print(x, "can not be uploded")
    if not flag:
        print("All your articles, were uploaded to TagTog!")
    else:
        print("Please check the PMID or your username, password and project name!")

def abstractwordcloud(finallist,pic,sw,basename):
    print("Creating WordCloud!")
    lemmatizer = nltk.stem.WordNetLemmatizer()
    stopwords = nltk.corpus.stopwords.words('english')
    morewords = ["supplementary","page","good","term","additional","bad","help","library","experimental","although","second","hour","minute","period","given","technique","equipment","per","day","cent","function","preparation","also",
"furthermore","may","cell","role","dna","rna","protein","size","action","study","level","gene","mrna","treatment","vitro","result","important","basic","acidic","rna","expression","cdna","thus","role","receptor","organ",
"mechanism","sequence","analysis","found","control","increase","decrease","response","manner","regulate","potential","manner","increased","decreased","small","large","production","pathway","growth","however",
"involved","well","investigated","finding","regulation","play","target","overexpression","association","associated","show","via","line","together","identified","expressed","done","peptide","remain","provide","suggest","reduction",
"test","full","known","novel","characterize","inhibited","inhibited","signaling","factor","multiple","reduced","activity",
"induced","including","overall","transcript","reversed","group","attenuated","showed","family","primary","mater",
"various","examined","member","blocked","exploration","effect","assay","type","addition","domain","demonstrated",
"present","using","inhibition","form","tissue","required","two","transcription","suggesting","vivo","activation",
"transcriptional","used","essential","normal","inhibitor","patient","new","activated","knockdown","data",
"complex","accumulation","compared","revealed","significant","significantly","molecular","loss","cellular",
"cause","ability","indicate","demonstrate","whereas","high","higher","lead","sample","genetic","variant","generation","risk",
"performed","population","reported","first","little","proccesing","load","identify","acid","number","residue",
"area","combined","viability","candidate","rapidly","intracellular","compound","research","stage",
"familial","promote","strong","binding","marker","region","recent","case","independent","bind","near",
"single","value","approximately","development","report","four","one","seven","dataset",
"contribute","lower","variation","control","confidence","unclear","processing","remains","substrate",
"following","insult","stop","write","unknown","animal","component","process","interaction","site","system",
"structure","shown","accompanied","disease","functional","precursor","polymorphism","distribution","model",
"several","observed","therefore","human","mouse","step","pattern","presence","different","induce",
"early","depletion","encoding","direct","within","contain","product","find","allowed","biological",
"formation","information","localization","change","specific","three","previously","enzyme","could","similar","many","regulate","distinct","moreover","phenotype","molecule",""]
    if len(sw) > 0:
        morewords += sw
    abstracts = [item[4] for item in finallist] # all abstarct to a nested list
    abstracts = [*map(str.lower, abstracts)] # all abstract to lower case
    words = []
    terms = []
    for x in abstracts:
        words += ([*map(str.lower, nltk.word_tokenize(x))])
    for z in morewords:
        stopwords.append(z)
    for word in words:
        if word not in stopwords and word.isalpha() and len(word) > 2:
            terms.append(word)
    lemmas = [lemmatizer.lemmatize(t) for t in terms]
    tokens = [w for w in lemmas if w not in stopwords]
    maskpic = np.array(Image.open(pic))
    image_colors = ImageColorGenerator(maskpic)
    wc = WordCloud(max_words=1000,background_color="white", mask=maskpic, stopwords=stopwords,regexp=r"\w[\w' ]+", random_state=1,margin=5)
    wc = wc.generate("+".join(tokens))
    default_colors = wc.to_array()
    wc.to_file(basename + "_WordCloud.png")
    plt.imshow(wc.recolor(color_func=grey_color_func, random_state=3),
interpolation="bilinear")
    plt.imshow(default_colors, interpolation="bilinear")
    plt.axis("off")
    plt.figure()
    plt.close()
    plt.close()
    return tokens, len(abstracts)




def plotcommon(tokens,number,basename):
    plt.rcParams["figure.figsize"] = (20,20)
    wordfreqdist = nltk.FreqDist(tokens)
    mostcommon = wordfreqdist.most_common(30)
    plt.barh(range(len(mostcommon)),[val[1] for val in mostcommon], align='center')
    plt.yticks(range(len(mostcommon)), [val[0] for val in mostcommon])
    title = "Number of Abstract: " +  str(number)
    plt.title(title)
    plt.savefig(basename + '_commonword.png')

#############

def setvars(arg):
    if arg.username != "":
        print("You decide to upload the abstracts to TagTog")
        tagtog = True
    else:
        print("You decide not to upload the abstracts to TagTog")
        tagtog = False
    if arg.password != "":
        pass
    else:
        if arg.username != "":
            print("You leave the password field empty. The abstract will not be uploaded to TagTog!")
            tagtog = False
    if arg.pubtator != "":
        print("The results of pubtators are keeped in ",arg.pubtator)
        pubtator = True 
    else:
        pubtator = False
        print("You decide not to run Pubtator")
    if arg.terms != "regex1\nregex2":
        if len(arg.terms.split(" ")) > 1:
            print("Error: there are spaces between terms, please separate only by newlines")
            sys.exit(0)
        else:
            terms = arg.terms.split("\n")
            print("You will filter by:",arg.terms)
    else:
        print("You decide not to filter by terms")
        terms = []
    if arg.stopwords != "word1\nword2":
        if len(arg.stopwords.split(" ")) > 1:
            print("Error: there are spaces between stopwrods, please separate only by newlines")
            sys.exit(0)
        else:
            sw = arg.stopwords.split("\n")
    else: 
        sw = []
    fileimg = os.path.join(os.path.dirname(__file__), './pics') + "/" + arg.img[0]
    return tagtog,pubtator,terms,sw,fileimg

#############

def main():
    arg = window()
    if arg.command == "Pre-Woody":
        if len(arg.genes.split(" ")) > 1:
            print("Error: there are spaces between IDs, please separate only by newlines")
            sys.exit(0)
        else:
            genes = arg.genes.split("\n")
        finallists = []
        for x in genes:
            print("Processing:",x)
            primarylist = get_text(x)
            if primarylist:
                pmids = get_list(primarylist)
                lista = [x] + [pmids]
                finallists.append(lista)
        df = pd.DataFrame(finallists, columns=["gene","id"])
        df.to_csv(arg.output,sep="\t",header=True,index=False)
    else:
        pd.set_option('precision', 0)
        # *Always* tell NCBI who you are
        Entrez.email = "anonymus@gmail.com"
        encoding_to_module = {'gzip': 'gzip','bzip2': 'bz2','xz': 'lzma'}
        df = pd.read_table(arg.pubmed,sep="\t",header=0)
        count = 0
        finallist = []
        finalpmids = []
        tagtog,pubtator,terms,sw,fileimg = setvars(arg)
        for row in df.itertuples():
            lg,pmids = filter_abstact(row.id,row.gene,terms)
            if len(lg) == 0:
                continue
            if pubtator:
                id_list,dfgp = get_pubtator(pmids,row.gene)
                if len(id_list) == 0:
                    finalpmids +=  pmids.split(",")
                    finallist += lg
                    print("Can not retrieve pubTator Tags")
                    continue
                if count == 0:
                    dfo = gene_info(id_list,dfgp)
                    count += 1
                else:
                    df = gene_info(id_list,dfgp)
                    dfo = pd.concat([dfo, df])
            finalpmids +=  pmids.split(",")
            finallist += lg
        if len(finallist) == 0:
            print("No abstarct founds! So Woody is done!")
            sys.exit(0)
        tokens,number  = abstractwordcloud(finallist,fileimg,sw,arg.basename)
        plotcommon(tokens,number,arg.basename)
        dflg = pd.DataFrame(finallist)
        if len(terms) >0:
            dflg.columns = "Gene","PMID","Journal","Title","Abastract","Term"
            dflg.to_csv(arg.basename + "_Abstarcts.tsv",sep="\t",header=True,index=False,columns=["Gene","PMID","Journal","Title","Term"])
        else:
            dflg.columns = "Gene","PMID","Journal","Title","Abastract"
            dflg.to_csv(arg.basename + "_Abstarcts.tsv",sep="\t",header=True,index=False,columns=["Gene","PMID","Journal","Title"])
        if pubtator:
            try:
                dfo = dfo.drop_duplicates()
                dfo.to_csv(arg.basename + "_PubTator.tsv",sep="\t",header=True,index=False)
            except:
                pass
        if tagtog:
            get_tagtog(finalpmids,arg.project,arg.username,arg.password)
