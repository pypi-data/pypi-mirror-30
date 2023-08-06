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
from collections import defaultdict

import biolib.seq_io as seq_io

from unitem.defaults import *
from unitem.common import (read_bins, 
                            parse_bin_stats, 
                            calculateN50L50M50)
from unitem.markers import Markers


class Greedy():
    """Perform greedy selection of genomes across multiple binning methods."""

    def __init__(self, bin_prefix):
        """Initialization."""
        
        self.logger = logging.getLogger('timestamp')
        
        self.bin_prefix = bin_prefix

    def _update_bins(self, bins, hq_binning_method, hq_bin_id):
        """Remove highest quality bin and scaffolds in this bin from all other bins."""
        
        hq_scaffolds = set(bins[hq_binning_method][hq_bin_id].keys())
        
        # remove highest quality bin
        del bins[hq_binning_method][hq_bin_id]
        if len(bins[hq_binning_method]) == 0:
            del bins[hq_binning_method]

        # remove scaffolds in highest quality bin from all other bins
        for method_id in bins:
            for bin_id in bins[method_id]:
                for scaffold_id in hq_scaffolds:
                    bins[method_id][bin_id].pop(scaffold_id, None)

    def _update_gene_tables(self, bins, gene_tables, hq_binning_method, hq_bin_id):
        """Remove scaffolds in highest quality bin from marker gene tables."""

        hq_scaffolds = set(bins[hq_binning_method][hq_bin_id].keys())

        # remove gene table for highest quality bin
        hq_bac_table, hq_ar_table = gene_tables[hq_binning_method]
        del hq_bac_table[hq_bin_id]
        del hq_ar_table[hq_bin_id]

        # remove scaffolds from highest quality bin from other bins
        for binning_method, (bac_gene_tables, ar_gene_tables) in gene_tables.iteritems():
            for bin_id in bac_gene_tables:
                for marker_id, scaffold_ids in bac_gene_tables[bin_id].iteritems():
                    bac_gene_tables[bin_id][marker_id] = []
                    for scaffold_id in scaffold_ids:
                        if scaffold_id not in hq_scaffolds:
                            bac_gene_tables[bin_id][marker_id].append(scaffold_id)
                            
                for marker_id, scaffold_ids in ar_gene_tables[bin_id].iteritems():
                    ar_gene_tables[bin_id][marker_id] = []
                    for scaffold_id in scaffold_ids:
                        if scaffold_id not in hq_scaffolds:
                            ar_gene_tables[bin_id][marker_id].append(scaffold_id)

    def run(self, profile_dir, bin_dirs, weight, min_quality, output_dir):
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
        
        markers = Markers()
        
        self.logger.info('Performing greedy bin selection with weight = %.1f and minimum quality = %.1f.' % (weight, min_quality))
        
        # get scaffold IDs in bins across all binning methods
        self.logger.info('Reading all bins.')
        bins = read_bins(bin_dirs)

        # get marker genes for bins across all binning methods
        self.logger.info('Identifying marker genes across all bins.')
        gene_tables = markers.marker_gene_tables(profile_dir)
        
        # get genomic and assembly statistics for all bins
        self.logger.info('Reading assembly statistics for all bins.')
        orig_bin_stats = parse_bin_stats(profile_dir)
        
        # perform greedy selection of bins
        fout = open(os.path.join(output_dir, 'selected_bins.tsv'), 'w')
        fout.write('UniteM Bin ID\tBinning Method\tBin ID\tMarker Set Domain\tCompleteness (%)\tContamination (%)\tQuality (%)')
        fout.write('\tGenome Size\tN50\tL50\tNo. Contigs\tNo. Filtered Contigs\n')
        
        bin_num = 0
        while True:
            # determine highest quality bin across all binning methods
            highest_quality = -1
            hq_bin = None
            hq_num_scaffolds = 0
            hq_genome_size = 0
            hq_n50 = None
            hq_m50 = None
            for binning_method, (bac_gene_tables, ar_gene_tables) in gene_tables.iteritems():
                for bin_id in bac_gene_tables:
                    domain, comp, cont = markers.evaluate(bac_gene_tables[bin_id], 
                                                            ar_gene_tables[bin_id])
                         
                    num_scaffolds = len(bins[binning_method][bin_id])
                    if num_scaffolds == 0:
                        continue
                        
                    genome_size = sum([len(seq) for seq in bins[binning_method][bin_id].values()])
                    
                    q = comp - weight*cont
                    if q < min_quality:
                        continue
                    elif q >= highest_quality:
                        n50, l50, m50 = calculateN50L50M50(bins[binning_method][bin_id].values())
                    
                    if (q > highest_quality 
                        or (q == highest_quality 
                                and n50 > hq_n50)
                        or (q == highest_quality 
                                and n50 == hq_n50
                                and genome_size > hq_genome_size)):

                        highest_quality = q
                        hq_num_scaffolds = num_scaffolds
                        hq_genome_size = genome_size
                        hq_n50 = n50
                        hq_m50 = m50
                        hq_bin = (binning_method, bin_id, domain, comp, cont, q, genome_size, num_scaffolds)

            if highest_quality < min_quality:
                break

            # report selection
            hq_bm, hq_bin_id, hq_domain, hq_comp, hq_cont, hq_quality, hq_gs, hq_num_scaffolds = hq_bin
            self.logger.info("Selected %s from %s with quality = %.1f (comp. = %.1f%%, cont. = %.1f%%)." % (hq_bin_id,
                                                                                                            hq_bm,
                                                                                                            hq_quality,
                                                                                                            hq_comp,
                                                                                                            hq_cont))
                
            # write out highest quality bin
            bin_num += 1
            unitem_bin_id = '%s_%d' % (self.bin_prefix, bin_num)
            bin_out = open(os.path.join(output_dir, unitem_bin_id + '.fna'), 'w')
            for seq_id, seq in bins[hq_bm][hq_bin_id].iteritems():
                bin_out.write('>' + seq_id + '\n')
                bin_out.write(seq + '\n')
            bin_out.close()

            # write out summary information about selected bins
            fout.write('%s\t%s\t%s\t%s\t%.2f\t%.2f\t%.2f' % (unitem_bin_id,
                                                                hq_bm, 
                                                                hq_bin_id, 
                                                                hq_domain, 
                                                                hq_comp, 
                                                                hq_cont, 
                                                                hq_quality))
                                                            
            orig_num_scaffolds = orig_bin_stats[hq_bm][hq_bin_id]['# scaffolds']
            n50, l50, m50 = calculateN50L50M50(bins[hq_bm][hq_bin_id].values())
            fout.write('\t%d\t%d\t%d\t%d\t%d\n' % (hq_gs,
                                                n50,
                                                l50,
                                                hq_num_scaffolds,
                                                orig_num_scaffolds - hq_num_scaffolds))

            # remove scaffolds in highest quality bin from marker gene tables
            self._update_gene_tables(bins, gene_tables, hq_bm, hq_bin_id)

            # remove scaffolds in highest quality bin from all other bins
            self._update_bins(bins, hq_bm, hq_bin_id)
            
        self.logger.info('Selected %d bins.' % bin_num)

        fout.close()
