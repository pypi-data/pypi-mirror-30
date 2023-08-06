###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import os
import logging
import itertools
import operator
from collections import defaultdict

from biolib.external.execute import check_on_path
import biolib.seq_io as seq_io

from unitem.defaults import *
from unitem.common import (read_bins, 
                            marker_gene_tables, 
                            parse_bin_stats, 
                            calculateN50L50M50)
from unitem.markers import Markers


class Majority():
    """Perform Markov 'majority vote' clustering across multiple binning methods."""

    def __init__(self, bin_prefix, cpus):
        """Initialization."""
        
        self.logger = logging.getLogger('timestamp')
        
        self.cpus = cpus
        self.bin_prefix = bin_prefix
        
        check_on_path('mcl')
        check_on_path('mcxload')
        
        self.graph_prefix = 'graph'
        
    def _contig_id_map(self, bins):
    
        # get all unique contigs across bins
        contigs = {}
        for binning_method in bins:
            for bin_id in bins[binning_method]:
                contigs.update(bins[binning_method][bin_id])
        self.logger.info('Identified %d unique contigs across all bins.' % len(contigs))
                
        # simplify contig names to integers
        contig_int_to_seq = {}
        contig_id_to_int = {}
        contig_int_to_id = {}
        for i, (contig_id, seq) in enumerate(contigs.iteritems()):
            contig_id_to_int[contig_id] = i
            contig_int_to_id[i] = contig_id
            contig_int_to_seq[i] = seq
            
        return contig_id_to_int, contig_int_to_id, contig_int_to_seq
        
    def _markers_on_contigs(self, gene_tables):
        """Get markers on each contig."""
        
        bac_markers = defaultdict(list)
        ar_markers = defaultdict(list)
        processed_contigs = set()
        for binning_method, (bac_gene_tables, ar_gene_tables) in gene_tables.iteritems():
            scaffolds_in_binning_method = set()
            for bin_id in bac_gene_tables:
                for marker_id, scaffold_ids in bac_gene_tables[bin_id].iteritems():
                    for scaffold_id in scaffold_ids:
                        if scaffold_id in processed_contigs:
                            continue
                        bac_markers[scaffold_id].append(marker_id)
                        
                    scaffolds_in_binning_method.update(scaffold_ids)
                            
            for bin_id in ar_gene_tables:
                for marker_id, scaffold_ids in ar_gene_tables[bin_id].iteritems():
                    for scaffold_id in scaffold_ids:
                        if scaffold_id in processed_contigs:
                            continue
                        ar_markers[scaffold_id].append(marker_id)
                        
                    scaffolds_in_binning_method.update(scaffold_ids)
                        
            processed_contigs.update(scaffolds_in_binning_method)
                
        return bac_markers, ar_markers
        
    def _create_graph(self, 
                        bins,
                        gene_tables,
                        min_votes,
                        graph_weight, 
                        graph_min_quality, 
                        contig_id_to_int, 
                        output_dir):
        """Create MCL graph in ABC format."""
        
        self.logger.info("Identifying edges with min. vote = %d, weight = %.1f, min. quality = %.1f." % (min_votes, graph_weight, graph_min_quality))
        
        markers = Markers()
        
        edges = defaultdict(int)
        for binning_method in bins:
            bac_gene_tables, ar_gene_tables = gene_tables[binning_method]
            for bin_id in bins[binning_method]:
                domain, comp, cont = markers.evaluate(bac_gene_tables[bin_id], 
                                                            ar_gene_tables[bin_id])
                q = comp-graph_weight*cont
                if q >= graph_min_quality:
                    sorted_seq_ids = sorted(bins[binning_method][bin_id].keys())
                    for edge1, edge2 in itertools.combinations(sorted_seq_ids, 2):
                        i1 = contig_id_to_int[edge1]
                        i2 = contig_id_to_int[edge2]
                        edges[(i1, i2)] += 1
                    
        self.logger.info('Writing edges to file.')
        abc_file = os.path.join(output_dir, '%s.abc' % self.graph_prefix)
        fout = open(abc_file, 'w')
        for edge, weight in sorted(edges.items(), key=operator.itemgetter(1), reverse=True):
            if weight >= min_votes:
                fout.write('%d\t%d\t%d\n' % (edge[0], edge[1], weight))
        fout.close()
        
        self.logger.info('Creating binary graph file.')
        tab_file = abc_file.replace('.abc', '.tab')
        mci_file = abc_file.replace('.abc', '.mci')
        cmd = 'mcxload --write-binary --stream-mirror -abc %s -write-tab %s -o %s' % (abc_file, tab_file, mci_file)
        os.system(cmd)
        
    def _cluster_graph(self, 
                        contig_int_to_id, 
                        contig_int_to_seq, 
                        bac_markers, 
                        ar_markers,
                        weight,
                        min_quality,
                        output_dir):
        """Partition graph using MCL algorithm."""
        
        markers = Markers()
        
        fout_summary = open(os.path.join(output_dir, 'summary.tsv'), 'w')
        fout_summary.write('I-value\tGenomes (Q>%.1f)\tCompleteness (%%)\tContamination (%%)\tQuality (%%)\n' % min_quality)

        # perform clustering
        for i_value in [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
            # perform clustering
            mci_graph_file = os.path.join(output_dir, self.graph_prefix + '.mci')
            output_file_binary = os.path.join(output_dir, 'clusters.I%.1f' % i_value)
            cmd = 'mcl %s -te %d -I %f -o %s' % (mci_graph_file, self.cpus, i_value, output_file_binary)
            os.system(cmd)
            
            # write out clusting in readable format
            tab_file = os.path.join(output_dir, self.graph_prefix + '.tab')
            output_file = os.path.join(output_dir, 'clusters.I%.1f.tab' % i_value)
            cmd = 'mcxdump -icl %s -tabr %s -o %s' % (output_file_binary, tab_file, output_file)
            os.system(cmd)
            
            # write out bins
            bin_dir = os.path.join(output_dir, 'bins.I%.1f' % i_value)
            if not os.path.exists(bin_dir):
                os.makedirs(bin_dir)
                
            fout_bin_summary = open(os.path.join(bin_dir, 'bin_summary.tsv'), 'w')
            fout_bin_summary.write('UniteM Bin ID\tMarker Set Domain\tCompleteness (%)\tContamination (%)\tQuality (%)\n')
            
            pass_q = 0               
            sum_comp = 0
            sum_cont = 0
            sum_q = 0
            bin_num = 0
            for line in open(output_file):
                line_split = line.strip().split()
                
                bin_num += 1
                bin_name = '%s_%d' % (self.bin_prefix, bin_num)
                fout = open(os.path.join(bin_dir, bin_name + '.fna'), 'w')
                bac_gene_table = defaultdict(list)
                ar_gene_table = defaultdict(list)
                for contig_int_id in line_split:
                    contig_int_id = int(contig_int_id)
                    contig_id = contig_int_to_id[contig_int_id]
                    fout.write('>%s\n' % contig_id)
                    fout.write('%s\n' % contig_int_to_seq[contig_int_id])
                    
                    for marker_id in bac_markers[contig_id]:
                        bac_gene_table[marker_id].append(contig_id)
                        
                    for marker_id in ar_markers[contig_id]:
                        ar_gene_table[marker_id].append(contig_id)
                fout.close()
                
                domain, comp, cont = markers.evaluate(bac_gene_table, 
                                                        ar_gene_table)
                                                            
                q = comp - weight*cont
                if False:
                    self.logger.info("Partitioned bin_%d with quality = %.1f (comp. = %.1f%%, cont. = %.1f%%)." % (bin_num,
                                                                                                                q, 
                                                                                                                comp,
                                                                                                                cont))
                fout_bin_summary.write('%s\t%s\t%.2f\t%.2f\t%.2f\n' % (bin_name,
                                                                        domain,
                                                                        comp,
                                                                        cont,
                                                                        q))
                                                                    
                if q > min_quality:
                    pass_q += 1              
                    sum_comp += comp
                    sum_cont += cont
                    sum_q += q
                                                                    
            self.logger.info('I = %.1f: %d genomes with total quality = %.1f (comp. = %.1f, cont. = %.1f)' % (i_value,
                                                                                                                pass_q,
                                                                                                                sum_q,
                                                                                                                sum_comp,
                                                                                                                sum_cont))
            fout_summary.write('%.1f\t%d\t%.1f\t%.1f\t%.1f\n' % (i_value,
                                                                    pass_q,
                                                                    sum_comp,
                                                                    sum_cont,
                                                                    sum_q))
                                                                    
            fout_bin_summary.close()
        fout_summary.close()
                
    def run(self, 
            profile_dir, 
            bin_dirs,
            min_votes,
            graph_weight,
            graph_min_quality,
            weight, 
            min_quality, 
            output_dir):
        """Perform greedy selection of genomes across multiple binning methods.

        Parameters
        ----------
        profile_dir : str
          Directory with bin profiles (output of 'profile' command).
        bin_dirs : list of str
            Directories containing bins from different binning methods.
        weight : float
          Weight given to contamination for assessing genome quality.
        min_quality : float
          Minimum quality of bin to retain.
        output_dir : str
          Output directory.
        """
        
        self.logger.info("Performing Markov 'majority vote' clustering with weight = %.1f and minimum quality = %.1f." % (weight, min_quality))
        
        # get scaffold IDs in bins across all binning methods
        self.logger.info('Reading all bins.')
        bins = read_bins(bin_dirs)
        
        # create mapping to contigs
        self.logger.info('Identifying unique contigs across all bins.')
        contig_id_to_int, contig_int_to_id, contig_int_to_seq = self._contig_id_map(bins)

        # get marker genes for bins across all binning methods
        self.logger.info('Identifying marker genes across all bins.')
        gene_tables = marker_gene_tables(profile_dir)
        
        # get markers on each scaffold
        bac_markers, ar_markers = self._markers_on_contigs(gene_tables)
        
        # get genomic and assembly statistics for all bins
        self.logger.info('Reading assembly statistics for all bins.')
        orig_bin_stats = parse_bin_stats(profile_dir)
        
        # create graph in ABC format
        self.logger.info('Creating graph across all binning methods.')
        self._create_graph(bins, 
                            gene_tables,
                            min_votes,                            
                            graph_weight, 
                            graph_min_quality, 
                            contig_id_to_int, 
                            output_dir)
        
        # cluster graph
        self.logger.info('Partitioning graph.')
        self._cluster_graph(contig_int_to_id, 
                            contig_int_to_seq,
                            bac_markers, 
                            ar_markers,
                            weight, 
                            min_quality,                         
                            output_dir)
        
        # write out summary of selected bins
        fout = open(os.path.join(output_dir, 'selected_bins.tsv'), 'w')
        fout.write('UniteM Bin ID\tBinning Method\tBin ID\tMarker Set Domain\tCompleteness (%)\tContamination (%)\tQuality (%)')
        fout.write('\tGenome Size\tN50\tL50\tNo. Scaffolds\tNo. Filtered Scaffolds\n')

        fout.close()
