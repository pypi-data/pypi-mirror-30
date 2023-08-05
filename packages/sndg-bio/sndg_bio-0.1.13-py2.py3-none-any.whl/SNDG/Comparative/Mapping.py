import os
from tqdm import tqdm
import pandas as pd

from SNDG import execute as e
from SNDG import  mkdir
from SNDG.Comparative.CoverageAnalysis import CoverageAnalysis



"""
requires:
samtools bcftools bowtie bedtools and bwa binaries in PATH
ncbi-blast+ installed
picard and gatk link in path:
example:
/usr/local/bin/gatk
#!/bin/bash
java -jar /opt/GATK/GenomeAnalysisTK.jar $@

bam2fastq --aligned --force --strict -o mapped#.fq [assembly.bam]

"""


class Mapping:

    @staticmethod
    def init_ref(path):
        cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(path))
            filename = os.path.basename(path)
            e("bwa index -a is  {record_name}".format(record_name=filename))
            e(
                "picard CreateSequenceDictionary R={record_name} O={record_name}.dict".format(record_name=filename))
            e("samtools faidx {record_name}".format(record_name=filename))
            #e("bowtie2-build {record_name} {record_name}".format(record_name=filename))
            e("makeblastdb -dbtype nucl -in {record_name} ".format(record_name=filename))
        finally:
            os.chdir(cwd)

    @staticmethod
    def alignment(work_dir,record, read1, read2,strain="sample1",species=None):
        if not species:
            species = strain
        # Quality control
        e("prinseq-lite -fastq {read1_full} -fastq2 {read2_full} -min_qual_mean 25 -trim_left 20 -trim_right 2 -trim_qual_right 25 -trim_qual_window 5 -min_len 35 -out_good trimmed".format(read1_full = read1, read2_full = read2))
        e("fastqc {wd}trimmed_1.fastq",wd=work_dir)
        e("fastqc {wd}trimmed_2.fastq",wd=work_dir)
        if args.singletons:
            e("cat trimmed_1_singletons.fastq >> trimmed_1.fastq")
            e("cat trimmed_2_singletons.fastq >> trimmed_2.fastq")
            os.remove("trimmed_1_singletons.fastq ")
            os.remove("trimmed_2_singletons.fastq")

        # Generate a SAM file containing aligned reads
        e("bwa mem -M -R \'@RG\\tID:group1\\tSM:{strain}\\tPL:illumina\\tLB:{species}\' {record_name} trimmed_1.fastq trimmed_2.fastq > aligned_reads.sam"
          .format(record_name = record,strain=strain,species=species))
        # Filter mapped reads and convert to BAM
        e("samtools view -F 4 -S -b -h aligned_reads.sam > mapped_reads.bam")
        e("samtools view -f 4 -S -b -h aligned_reads.sam > unmapped_reads.bam")
        os.remove("aligned_reads.sam")
        # Convert back to FASTQ for quality control
        e("samtools fastq mapped_reads.bam > mapped_reads.fastq")
        e("fastqc mapped_reads.fastq")
        # Sort and mark duplicates
        e("java -jar $PICARD SortSam INPUT=mapped_reads.bam OUTPUT=sorted_reads.bam SORT_ORDER=coordinate")
        e("java -jar $PICARD MarkDuplicates INPUT=sorted_reads.bam OUTPUT=dedup_reads.bam METRICS_FILE=metrics.txt")
        e("java -jar $PICARD BuildBamIndex INPUT=dedup_reads.bam")

        return "dedup_reads.bam"

    @staticmethod
    def variant_call(record,alignment,strain):
        # Call variants in the sequence data
        e("java -jar $GATK -T HaplotypeCaller -R {record_name} -I {alignment} -gt_mode DISCOVERY -ploidy 1 -stand_call_conf 30 -o raw_variants.vcf"
          .format(record_name = record,alignment=alignment))
        # Apply hard filters to a call set
        e("java -jar $GATK -T SelectVariants -R {record_name} -V raw_variants.vcf  -selectType SNP -o raw_snps.vcf".format(record_name = record))
        e("java -jar $GATK -T VariantFiltration -R {record_name} -V raw_snps.vcf  -filter \"QD < 2.0 || FS > 60.0 || MQ < 40.0 || MQRankSum < -12.5 || ReadPosRankSum < -8.0\" --filterName \"my_snp_filter\" -o filtered_snps.vcf".format(record_name = record))
        e("java -jar $GATK -T SelectVariants -R {record_name} -V raw_variants.vcf  -selectType INDEL -o raw_indels.vcf".format(record_name = record))
        e("java -jar $GATK -T VariantFiltration -R {record_name} -V raw_indels.vcf  -filter \"QD < 2.0 || FS > 200.0 || ReadPosRankSum < -20.0\" --filterName \"my_indel_filter\" -o filtered_indels.vcf".format(record_name = record))
        e("java -jar $GATK -T CombineVariants --assumeIdenticalSamples -R {record_name} -V filtered_snps.vcf -V filtered_indels.vcf -genotypeMergeOptions UNIQUIFY -o concatenated.vcf".format(record_name = record))
        # e("sed \'/^#[^#]/ {{s/\\tsample1\\.variant2//}}\' concatenated.vcf > %s.vcf" % '_'.join(read1.split('_')[:2])) # Removes column from vcf header
        return strain + ".vcf"


    @staticmethod
    def realign(bam_file, ref_fasta):
        out_bwa_bam = "sorted_" + bam_file
        e("samtools sort -o %s %s" % (out_bwa_bam, bam_file))
        out_bwa_final_bam = "realigned2_" + bam_file
        out_bwa_intervals = bam_file + ".intervals"
        out_bwa_intervals2 = bam_file + ".intervals"
        bwa_realigned = "realigned_" + bam_file
        duplicates = "duplicates_" + bam_file
        bwa_iter1 = "iter1_" + bam_file
        if not os.path.exists(out_bwa_final_bam):
            e("samtools index %s" % out_bwa_bam)
            e("gatk -T RealignerTargetCreator -R {ref} -I {input} -o {out}",
                    ref=ref_fasta, input=out_bwa_bam, out=out_bwa_intervals)
            e("gatk -T IndelRealigner -R {ref} -I {input} -targetIntervals {intervals} -o {output}",
                    ref=ref_fasta, input=out_bwa_bam, intervals=out_bwa_intervals, output=bwa_realigned)
            # Aca se recomienda correr el BaseRecalibrator de GATK pero no se tiene un vcf con variantes comunes
            e("picard MarkDuplicates I={input}   REMOVE_DUPLICATES=true O={output} M={duplicates}",
                    input=bwa_realigned, output=bwa_iter1, duplicates=duplicates)
            e("samtools index {input}", input=bwa_iter1)
            e("gatk -T RealignerTargetCreator -R {ref} -I {input} -o {intervals}",
                    ref=ref_fasta, input=bwa_iter1, intervals=out_bwa_intervals2)
            e("gatk -T IndelRealigner -R {ref} -I {input} -targetIntervals {intervals} -o {output}",
                    ref=ref_fasta, input=bwa_iter1, intervals=out_bwa_intervals2, output=out_bwa_final_bam)
            e("samtools index %s" % out_bwa_final_bam)

        for x in [bam_file, out_bwa_intervals, out_bwa_intervals2, bwa_realigned, bwa_iter1, bwa_iter1 + ".bai"]:
            if os.path.exists(x):
                os.remove(x)

        return out_bwa_final_bam

    @staticmethod
    def process_strain(ref_fasta, strain, read_paths, work_dir):
        """

       :param ref_fasta:
       :param strain:
       :param read_paths: tuple with paths of (path_r1,path_r2,path_singles)
       :param work_dir:
       :return:
        """

        out_bwa_bam = "final_bwa.bam"
        out_bwa_bam_idx = out_bwa_bam + ".bai"
        cwd = os.getcwd()
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        try:
            os.chdir(work_dir)

            out_bwa_pe = "bwa_pe.sam"
            out_bwa_pe_bam = "bwa_pe.bam"
            out_unmapped_pe_bam = "unmapped.bam"

            if not os.path.exists(out_bwa_bam_idx) and not os.path.exists(out_bwa_pe_bam):
                e(
                    'bwa mem -R "@RG\\tID:illumina\\tSM:{ncepa}\\tLB:{ncepa}"  {ref_fasta} {pe1} {pe2}  >  ' + out_bwa_pe,
                    ref_fasta=ref_fasta, ncepa=strain,
                    pe1=read_paths[0],
                    pe2=read_paths[1])
                e("samtools view -F 4 -Sbh %s > %s" % (out_bwa_pe, out_bwa_pe_bam))
                e("samtools view -f 4 -Sbh %s > %s" % (out_bwa_pe, out_unmapped_pe_bam))
                unmapped_pair_1 = "unmapped_pair_1.fastq"
                unmapped_pair_2 = "unmapped_pair_2.fastq"
                e("bedtools bamtofastq -i {ubam} -fq {upair}   -fq2 {upair2}",
                        upair2=unmapped_pair_2, upair=unmapped_pair_1, ubam=out_unmapped_pe_bam)
                out_bwa_pe_bam = Mapping.realign(out_bwa_pe_bam, ref_fasta)

            for x in [out_bwa_pe, out_unmapped_pe_bam]:
                if os.path.exists(x):
                    os.remove(x)

            out_bwa_se = "bwa_se.sam"
            out_bwa_se_bam = "bwa_se.bam"
            out_unmapped_se_bam = "unmapped_se.bam"
            if not os.path.exists(out_bwa_bam_idx) and not os.path.exists(out_bwa_se_bam):
                e('bwa mem -R "@RG\\tID:illumina\\tSM:{ncepa}\\tLB:{ncepa}"  {ref_fasta} {s1}   >  ' + out_bwa_se,
                        ref_fasta=ref_fasta, ncepa=strain,
                        s1=read_paths[2])
                e("samtools view -F 4 -Sbh %s > %s" % (out_bwa_se, out_bwa_se_bam))
                e("samtools view -f 4 -Sbh %s > %s" % (out_bwa_se, out_unmapped_se_bam))

                unmapped_single = "unmapped_single.fastq"
                e("bedtools bamtofastq -i {ubam} -fq {upair}   ",
                        upair=unmapped_single, ubam=out_unmapped_se_bam)
                out_bwa_se_bam = Mapping.realign(out_bwa_se_bam, ref_fasta)

            for x in [out_bwa_se, out_unmapped_se_bam]:
                if os.path.exists(x):
                    os.remove(x)

            out_bwa_raw_bam = "bwa_raw.bam"
            out_bwa_fm_bam = "bwa_fm.bam"
            out_bwa_fm_sort_bam = "bwa_fm_sort.bam"

            if not os.path.exists(out_bwa_bam_idx):
                e("samtools merge %s %s %s " % (out_bwa_raw_bam, out_bwa_pe_bam, out_bwa_se_bam))
                e("samtools sort -n -o %s %s" % (out_bwa_fm_sort_bam, out_bwa_raw_bam))
                e("samtools fixmate  %s %s" % (out_bwa_fm_sort_bam, out_bwa_fm_bam))
                e("samtools sort -o %s %s" % (out_bwa_bam, out_bwa_fm_bam))
                e("samtools index %s" % out_bwa_bam)

            for x in [out_bwa_raw_bam, out_bwa_fm_bam, out_bwa_fm_sort_bam,
                      out_bwa_pe_bam, out_bwa_se_bam, out_bwa_pe_bam + ".bai", out_bwa_se_bam + ".bai"]:
                if os.path.exists(x):
                    os.remove(x)

            if not os.path.exists("flagstat.txt"):
                e("samtools flagstat %s > %s" % (out_bwa_bam, "flagstat.txt"))
        finally:
            os.chdir(cwd)

    @staticmethod
    def bam_stats(strains, bamlist, reads_df=pd.DataFrame()):
        rows = []
        with tqdm(zip(strains, bamlist)) as pbar:
            for strain, in_bam in pbar:
                pbar.set_description(strain)
                ca = CoverageAnalysis(depth_path="/tmp/depth_" + strain + ".txt",min_depth=5)
                if ca.depth_df.empty:
                    ca.run_sdepth(in_bam)

                rows.append((strain, ca.horizontal_coverage(), ca.aligned_reads(in_bam),))
        df = pd.DataFrame.from_records(rows, columns=["strain", "hcov", "map_reads"])

        if not reads_df.empty:

            df = pd.merge( reads_df, df, on=["strain"])
            df["umap_reads"] = df["f_readcount"] - df["map_reads"]

        return df

    @staticmethod
    def variant_call(in_bam, ref_fasta, snpeffdb, work_dir="./", cpus=1):
        mkdir(work_dir)
        variants_file = work_dir + "/variants.vcf"
        variants_ann_file = work_dir + "/variants.ann.vcf"

        if not os.path.exists(variants_file):
            e(
                "gatk -T HaplotypeCaller -ploidy 1 -R {ref} -I {aln} --num_cpu_threads_per_data_thread {cpus} --genotyping_mode DISCOVERY -stand_call_conf 30 -o {vcf}",
                ref=ref_fasta, aln=in_bam, vcf=variants_file, cpus=cpus)
        if not os.path.exists(variants_ann_file):
            e("snpEff {database} {input} > {output}",
                    database=snpeffdb, input=variants_file, output=variants_ann_file)

    @staticmethod
    def vcf_stats(in_vcf):
        pass


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description = 'Mapping to variant calls pipeline.')
    required = parser.add_argument_group('required arguments')
    required.add_argument('-R', '--reference', action = 'store', dest = 'reference', required = True)
    required.add_argument('-A', '--annotation', action = 'store', dest = 'annotation', required = True)
    required.add_argument('-S', '--strain', action = 'store', dest = 'strain', default = "sample")
    required.add_argument('-R1', '--read1', action = 'store', dest = 'read1', required = True)
    required.add_argument('-R2', '--read2', action = 'store', dest = 'read2', required = True)
    parser.add_argument('--useSingletons', action = 'store_true', dest = 'singletons')

    args = parser.parse_args()

    Mapping.init_ref(args.reference)
    alignment_path = Mapping.alignment(args.reference,args.read1,args.read2,args.strain)
    Mapping.variant_call(args.reference,alignment_path)