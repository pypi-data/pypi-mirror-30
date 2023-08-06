import pandas as pd
import requests

from collections import defaultdict
from orangecontrib.bioinformatics.go import Ontology, Annotations

from orangecontrib.bioinformatics.geneset import GeneSets, GeneSet, GO_TERM_LINK


def jaccard_index(set1, set2):
    return round((len(set1.intersection(set2)) / len(set1.union(set2))) * 100, 2)


def go():
    df = pd.ExcelFile('/Users/jakakokosar/OneDrive/Documents/Orange/aplisiya/annotations.xlsx')
    data = df.parse("Annotated")
    map_go_to_genes = defaultdict(list)

    for index, row in data.iterrows():
        gene_id = row['GeneID']
        set1 = set()
        set2 = set()

        if isinstance(row['go_ids_left'], str):
            set1 = set(row['go_ids_left'].strip().split(';')[:-1])

        if isinstance(row['go_ids_right'], str):
            set2 = set(row['go_ids_right'].strip().split(';')[:-1])

        go_ids = set1.union(set2)

        for go_id in go_ids:
            map_go_to_genes[go_id].append(gene_id)

    ontology = Ontology()
    category = {'biological_process': 'Process',
                'molecular_function': 'Function',
                'cellular_component': 'Component'}

    lines = []
    for go, genes in map_go_to_genes.items():
        go_id = 'GO:' + go

        if 'is_obsolete' not in ontology[go_id].values:
            for gene in set(genes):
                lines.append(
                    ['6500', gene, go_id, 'ND', '-', ontology[go_id].values['name'],
                     '-', category[ontology[go_id].values['namespace']]]
                )

    with open('/Users/jakakokosar/OneDrive/Documents/Orange/gene_association.6500', 'w') as file:
        file.write('#tax_id\tGeneID\tGO_ID\tEvidence\tQualifier\tGO_term\tPubMed\tCategory\n')
        file.writelines('\t'.join(i) + '\n' for i in lines)


def go_gene_sets():
    """ Returns gene sets from GO.
    """

    ontology = Ontology()
    annotations = Annotations('6500', ontology=ontology)

    gene_sets_p = []
    gene_sets_f = []
    gene_sets_c = []
    for termn, term in ontology.terms.items():
        genes = annotations.get_genes_by_go_term(termn)
        hier = ('GO', term.namespace)
        if len(genes) > 0:

            gs = GeneSet(gs_id=termn, name=term.name, genes=genes, hierarchy=hier,
                         organism='6500', link=GO_TERM_LINK.format(termn))

            if term.namespace == 'biological_process':
                gene_sets_p.append(gs)
            if term.namespace == 'molecular_function':
                gene_sets_f.append(gs)
            if term.namespace == 'cellular_component':
                gene_sets_c.append(gs)

    bio_p = GeneSets(gene_sets_p)
    mol_f = GeneSets(gene_sets_f)
    cel_c = GeneSets(gene_sets_c)

    bio_p.to_gmt_file_format('/Users/jakakokosar/OneDrive/Documents/Orange/aplisiya/biological_process.gmt')
    mol_f.to_gmt_file_format('/Users/jakakokosar/OneDrive/Documents/Orange/aplisiya/molecular_function.gmt')
    cel_c.to_gmt_file_format('/Users/jakakokosar/OneDrive/Documents/Orange/aplisiya/cellular_component.gmt')


def kegg():
    df = pd.ExcelFile('/Users/jakakokosar/OneDrive/Documents/Orange/aplisiya/annotations.xlsx')
    data = df.parse("Annotated")
    ko_map = {}
    map_kegg_to_genes = defaultdict(list)

    for index, row in data.iterrows():
        gene_id = row['GeneID']
        set1 = set()
        set2 = set()

        if isinstance(row['kegg_ids_left'], str):
            set1 = set(row['kegg_ids_left'].strip().split(';')[:-1])

        if isinstance(row['kegg_ids_right'], str):
            set2 = set(row['kegg_ids_right'].strip().split(';')[:-1])

        kegg_ids = set1.union(set2)

        for go_id in kegg_ids:
            map_kegg_to_genes[go_id].append(gene_id)

    with requests.get("http://rest.kegg.jp/list/ko") as data:
        lines = data.text.split('\n')
        for line in lines:
            kegg_info = line.split('\t')
            try:
                ko_map[kegg_info[0]] = kegg_info[1]
            except IndexError:
                pass
                print(line, kegg_info)
                #raise

    genesets = []

    for kegg_id, genes in map_kegg_to_genes.items():
        kegg_id = 'ko:' + kegg_id

        if kegg_id in ko_map:
            kegg_name, kegg_description = ko_map[kegg_id].split(';', 1)

            gs = GeneSet(gs_id=kegg_id,
                         name=kegg_name,
                         description=kegg_description,
                         genes=genes,
                         hierarchy=('KEGG', 'orthologs'),
                         organism='6500',
                         link='http://www.kegg.jp/entry/{}'.format(kegg_id))

            genesets.append(gs)

    g_sets = GeneSets(genesets)
    g_sets.to_gmt_file_format('/Users/jakakokosar/OneDrive/Documents/Orange/aplisiya/kegg_genesets.gmt')


if __name__ == '__main__':
    #go()
    go_gene_sets()
    #kegg()


#data.to_csv('~/Documents/go_ids_analysis.tab', sep='\t', encoding='utf-8')



gos = ['0001889','0001892','0003690','0006338','0019904','0030154','0030225','0042267',
       '0000122','0001892','0003700','0005515','0006366','0008203','0030099','0035189','0046982',
       '0046983','0005667','0006953','0016071','0030324','0042267','0042803','0043565','0045669',
       '0048469','0000122','0008134','0016071','0019048','0019904','0045600','0045739','0048839','0050872','0050873']
