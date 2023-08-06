import os
import sys
import shutil
from annogesiclib.helper import Helper
from annogesiclib.multiparser import Multiparser
from annogesiclib.converter import Converter
from annogesiclib.combine_frag_tex import combine
from annogesiclib.stat_TA_comparison import stat_ta_tss, stat_ta_gff
from annogesiclib.transcript_detection import detect_transcript
from annogesiclib.fill_gap import fill_gap, longer_ta
from annogesiclib.gen_table_tran import gen_table_transcript
from annogesiclib.compare_tran_term import compare_term_tran
from annogesiclib.plot_tran import plot_tran
from annogesiclib.reorganize_table import reorganize_table


class TranscriptDetection(object):
    '''doing for transcript detection'''

    def __init__(self, args_tran):
        self.multiparser = Multiparser()
        self.helper = Helper()
        self.converter = Converter()
        self.gff_outfolder = os.path.join(args_tran.out_folder, "gffs")
        self.tran_path = os.path.join(self.gff_outfolder, "tmp")
        self.stat_path = os.path.join(args_tran.out_folder, "statistics")
        self.tmps = {"gff": "tmp.gff", "merge": "tmp_merge",
                     "tran": os.path.join(args_tran.out_folder, "tmp_tran"),
                     "tss_ta": os.path.join(self.gff_outfolder, "tmp_tss_ta"),
                     "ta_tss": os.path.join(self.gff_outfolder, "tmp_ta_tss"),
                     "ta_gff": os.path.join(self.gff_outfolder, "tmp_ta_gff"),
                     "gff_ta": os.path.join(self.gff_outfolder, "tmp_gff_ta"),
                     "uni": os.path.join(self.gff_outfolder, "tmp_uni"),
                     "overlap": os.path.join(
                         self.gff_outfolder, "tmp_overlap")}
        self.frag = "transcript_fragment.gff"
        self.tex = "transcript_tex_notex.gff"
        self.endfix_tran = "transcript.gff"

    def _compute_transcript(self, wig_f, wig_r, wig_folder, wig_type, strain,
                            libs, args_tran):
        print("Computing transcripts for {0}".format(strain))
        out = os.path.join(args_tran.out_folder, "_".join([strain, wig_type]))
        detect_transcript(wig_f, wig_r, wig_folder, libs, out, wig_type, args_tran)

    def _compute(self, wig_type, wigs, libs, args_tran):
        strains = []
        wig_folder = os.path.join(wigs, "tmp")
        for wig in os.listdir(wig_folder):
            if wig.endswith("_forward.wig"):
                strains.append(wig.replace("_forward.wig", ""))
        for strain in strains:
            f_file = os.path.join(wig_folder, "_".join(
                [strain, "forward.wig"]))
            r_file = os.path.join(wig_folder, "_".join(
                [strain, "reverse.wig"]))
            self._compute_transcript(f_file, r_file, wigs, wig_type,
                                     strain, libs, args_tran)
        return strains

    def _compare_tss(self, tas, args_tran):
        self.multiparser.parser_gff(args_tran.compare_tss, "TSS")
        self.multiparser.combine_gff(
                self.gff_outfolder,
                os.path.join(args_tran.compare_tss, "tmp"),
                "transcript", "TSS")
        print("Comaring of transcripts and TSSs")
        tss_folder = os.path.join(args_tran.compare_tss, "tmp")
        for ta in tas:
            ta_file = os.path.join(self.gff_outfolder,
                                   "_".join([ta, self.endfix_tran]))
            stat_tss_out = os.path.join(
                    self.stat_path, "".join([
                        "stat_compare_transcript_TSS_",
                        ta, ".csv"]))
            for tss in os.listdir(tss_folder):
                filename = tss.split("_TSS")
                if (filename[0] == ta) and (tss.endswith(".gff")):
                    stat_ta_tss(ta_file, os.path.join(tss_folder, tss),
                                stat_tss_out, self.tmps["ta_tss"],
                                self.tmps["tss_ta"], args_tran.fuzzy)
                    os.remove(ta_file)
                    os.remove(os.path.join(tss_folder, tss))
                    self.helper.sort_gff(self.tmps["ta_tss"], ta_file)
                    self.helper.sort_gff(
                            self.tmps["tss_ta"], os.path.join(
                                args_tran.compare_tss, tss))
                    os.remove(self.tmps["tss_ta"])
                    os.remove(self.tmps["ta_tss"])

    def _compare_cds(self, tas, args_tran):
        self.multiparser.parser_gff(args_tran.gffs, None)
        self.multiparser.combine_gff(
            self.gff_outfolder, os.path.join(args_tran.gffs, "tmp"),
            "transcript", None)
        print("Comaring of transcripts and genome annotations")
        cds_folder = os.path.join(args_tran.gffs, "tmp")
        for ta in tas:
            ta_file = os.path.join(self.gff_outfolder,
                                   "_".join([ta, self.endfix_tran]))
            stat_gff_out = os.path.join(self.stat_path, "".join([
                "stat_compare_transcript_genome_", ta, ".csv"]))
            for gff in os.listdir(cds_folder):
                if (gff[:-4] == ta) and (gff.endswith(".gff")):
                    cds_file = os.path.join(cds_folder, gff)
                    stat_ta_gff(ta_file, cds_file, stat_gff_out,
                                self.tmps["ta_gff"], self.tmps["gff_ta"],
                                args_tran.c_feature)
                    os.remove(ta_file)
                    os.remove(os.path.join(args_tran.gffs, gff))
                    self.helper.sort_gff(self.tmps["ta_gff"], ta_file)
                    self.helper.sort_gff(self.tmps["gff_ta"], os.path.join(
                        args_tran.gffs, gff))
                    os.remove(self.tmps["ta_gff"])
                    os.remove(self.tmps["gff_ta"])

    def _compare_tss_cds(self, tas, args_tran):
        '''compare transcript with CDS and TSS'''
        if (args_tran.compare_tss is not None) and (
                args_tran.c_feature is not None):
            self.multiparser.parser_gff(self.gff_outfolder, "transcript")
            self._compare_cds(tas, args_tran)
            self._compare_tss(tas, args_tran)
        elif (args_tran.c_feature is not None) and (
                args_tran.compare_tss is None):
            self.multiparser.parser_gff(self.gff_outfolder, "transcript")
            self._compare_cds(tas, args_tran)
        elif (args_tran.c_feature is None) and (
                args_tran.compare_tss is not None):
            self.multiparser.parser_gff(self.gff_outfolder, "transcript")
            self._compare_tss(tas, args_tran)

    def _for_one_wig(self, type_, args_tran):
        '''running transcript detection to one type of wig files'''
        if type_ == "tex_notex":
            libs = args_tran.tlibs
            wigs = args_tran.tex_wigs
        else:
            libs = args_tran.flibs
            wigs = args_tran.frag_wigs
        print("Importing {0} wig files".format(type_))
        strains = self._compute(type_, wigs, libs, args_tran)
        for strain in strains:
            out = os.path.join(self.gff_outfolder, "_".join([
                strain, "transcript", type_ + ".gff"]))
            self.helper.sort_gff(os.path.join(args_tran.out_folder,
                                 "_".join([strain, type_])), out)
            os.remove(os.path.join(args_tran.out_folder,
                                   "_".join([strain, type_])))
        return strains

    def _for_two_wigs(self, strains, args_tran):
        '''merge the results of fragemented and tex treated libs'''
        if (args_tran.frag_wigs is not None) and (
                args_tran.tex_wigs is not None):
            print("Merging fragmented and tex treated ones")
            for strain in strains:
                frag_gff = os.path.join(self.gff_outfolder,
                                        "_".join([strain, self.frag]))
                tex_gff = os.path.join(self.gff_outfolder,
                                       "_".join([strain, self.tex]))
                final_gff = os.path.join(self.gff_outfolder,
                                         "_".join([strain, self.endfix_tran]))
                for gff in os.listdir(self.gff_outfolder):
                    if "_transcript_" in gff:
                        filename = gff.split("_transcript_")
                        if (strain == filename[0]) and (
                                "tex_notex.gff" == filename[1]):
                            tex_file = gff
                        elif (strain == filename[0]) and (
                                "fragment.gff" == filename[1]):
                            frag_file = gff
                combine(os.path.join(self.gff_outfolder, frag_file),
                        os.path.join(self.gff_outfolder, tex_file),
                        args_tran.tolerance,
                        os.path.join(self.gff_outfolder,
                                     "_".join([strain, self.endfix_tran])))
                os.remove(frag_gff)
                os.remove(tex_gff)
        else:
            if args_tran.frag_wigs is not None:
                for strain in strains:
                    frag_gff = os.path.join(
                            self.gff_outfolder, "_".join([strain, self.frag]))
                    final_gff = os.path.join(
                            self.gff_outfolder,
                            "_".join([strain, self.endfix_tran]))
                    shutil.move(frag_gff, final_gff)
            elif args_tran.tex_wigs is not None:
                for strain in strains:
                    tex_gff = os.path.join(
                            self.gff_outfolder, "_".join([strain, self.tex]))
                    final_gff = os.path.join(
                            self.gff_outfolder,
                            "_".join([strain, self.endfix_tran]))
                    shutil.move(tex_gff, final_gff)

    def _post_modify(self, tas, args_tran):
        '''modify the transcript by comparing with genome annotation'''
        for ta in tas:
            for gff in os.listdir(args_tran.gffs):
                if (".gff" in gff) and (gff[:-4] == ta):
                    break
            print("Modifying {0} by refering to {1}".format(ta, gff))
            fill_gap(os.path.join(args_tran.gffs, gff),
                     os.path.join(self.tran_path,
                     "_".join([ta, self.endfix_tran])),
                     "overlap", self.tmps["overlap"], args_tran.modify)
            fill_gap(os.path.join(args_tran.gffs, gff),
                     os.path.join(self.tran_path,
                     "_".join([ta, self.endfix_tran])),
                     "uni", self.tmps["uni"], args_tran.modify)
            tmp_merge = os.path.join(self.gff_outfolder, self.tmps["merge"])
            if self.tmps["merge"] in self.gff_outfolder:
                os.remove(tmp_merge)
            self.helper.merge_file(self.tmps["overlap"], tmp_merge)
            self.helper.merge_file(self.tmps["uni"], tmp_merge)
            tmp_out = os.path.join(self.gff_outfolder, "_".join(["tmp", ta]))
            self.helper.sort_gff(tmp_merge, tmp_out)
            os.remove(self.tmps["overlap"])
            os.remove(self.tmps["uni"])
            os.remove(tmp_merge)
            final_out = os.path.join(self.gff_outfolder,
                                     "_".join(["final", ta]))
            longer_ta(tmp_out, args_tran.length, final_out)
            shutil.move(final_out,
                        os.path.join(self.tmps["tran"],
                                     "_".join([ta, self.endfix_tran])))
            os.remove(tmp_out)
        shutil.rmtree(self.gff_outfolder)
        shutil.move(self.tmps["tran"], self.gff_outfolder)

    def _remove_file(self, args_tran):
        if "tmp_wig" in os.listdir(args_tran.out_folder):
            shutil.rmtree(os.path.join(args_tran.out_folder, "tmp_wig"))
        if "merge_wigs" in os.listdir(args_tran.out_folder):
            shutil.rmtree(os.path.join(args_tran.out_folder, "merge_wigs"))
        self.helper.remove_tmp_dir(args_tran.gffs)
        self.helper.remove_tmp_dir(args_tran.compare_tss)
        self.helper.remove_tmp_dir(args_tran.terms)
        self.helper.remove_tmp(os.path.join(args_tran.out_folder, "gffs"))
        self.helper.remove_tmp(self.gff_outfolder)

    def _compare_term_tran(self, args_tran):
        '''searching the associated terminator to transcript'''
        if args_tran.terms is not None:
            print("Comparing between terminators and transcripts")
            self.multiparser.parser_gff(args_tran.terms, "term")
            if args_tran.gffs is not None:
                self.multiparser.combine_gff(
                    args_tran.gffs,
                    os.path.join(args_tran.terms, "tmp"), None, "term")
            compare_term_tran(self.gff_outfolder,
                              os.path.join(args_tran.terms, "tmp"),
                              args_tran.fuzzy_term, args_tran.fuzzy_term,
                              args_tran.out_folder, "transcript",
                              args_tran.terms, self.gff_outfolder)

    def _re_table(self, args_tran):
        for gff in os.listdir(self.gff_outfolder):
            if os.path.isfile(os.path.join(self.gff_outfolder, gff)):
                reorganize_table(args_tran.libs, args_tran.merge_wigs,
                                 "Coverage_details",
                                 os.path.join(args_tran.out_folder, "tables",
                                              gff.replace(".gff", ".csv")))

    def run_transcript(self, args_tran):
        if (args_tran.frag_wigs is None) and (args_tran.tex_wigs is None):
            print("Error: There is no wigs file!\n")
            sys.exit()
        if args_tran.frag_wigs is not None:
            strains = self._for_one_wig("fragment", args_tran)
        if args_tran.tex_wigs is not None:
            strains = self._for_one_wig("tex_notex", args_tran)
        self._for_two_wigs(strains, args_tran)
        tas = []
        if "none" not in args_tran.modify:
            for gff in os.listdir(args_tran.gffs):
                if gff.endswith(".gff"):
                    self.helper.sort_gff(os.path.join(args_tran.gffs, gff),
                                         self.tmps["gff"])
                    shutil.move(self.tmps["gff"],
                                os.path.join(args_tran.gffs, gff))
            self.multiparser.combine_gff(args_tran.gffs, os.path.join(
                args_tran.gffs, "tmp"), None, None)
            self.multiparser.parser_gff(self.gff_outfolder, "transcript")
            self.multiparser.combine_gff(args_tran.gffs, self.tran_path,
                                         None, "transcript")
            self.helper.check_make_folder(self.tmps["tran"])
            for ta in os.listdir(self.tran_path):
                if ta.endswith(".gff"):
                    if os.path.getsize(os.path.join(self.tran_path, ta)) != 0:
                        tas.append(ta.replace("_" + self.endfix_tran, ""))
            self._post_modify(tas, args_tran)
        self._compare_tss_cds(tas, args_tran)
        self._compare_term_tran(args_tran)
        print("Generating tables for the details")
        gen_table_transcript(self.gff_outfolder, args_tran)
        plot_tran(self.gff_outfolder, self.stat_path, args_tran.max_dist)
        self._re_table(args_tran)
        self._remove_file(args_tran)
