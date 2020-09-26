MOTIF_F := 'A[AGT]TAAA.{12,17}GG'
MOTIF_R := 'CC.{12,17}TTTA[TCA]T'
BUILD := hg38
OUT := sites sites_start pas pas_start intersect
#OUT := intersect

REFERENCE := $(BUILD).fa
SIZES := $(BUILD).chrom.sizes
ANNOTATION := gencode.v35.polyAs.gff3.gz
FILTER := 'polyA_signal'

REFRENCE_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(REFERENCE).gz
SIZES_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(SIZES)
ANNOTAION_URL := ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_35/$(ANNOTATION)

STRAND := f r


OUT_FILES := \
  $(foreach O, $(OUT), \
    $(foreach S, $(STRAND), \
      $(addprefix $(BUILD)_, \
        $(addsuffix _$S.bed, $O))))


.PHONY: all clean distclean


all: $(OUT_FILES)

clean:
	rm -f $(OUT_FILES)

distclean: clean
	rm -f $(REFERENCE) $(SIZES) $(ANNOTATION)


$(REFERENCE):
	wget $(REFRENCE_URL) && gunzip $@.gz

$(SIZES):
	wget $(SIZES_URL)

$(ANNOTATION):
	wget $(ANNOTAION_URL)


%.bed: %.raw
	echo 'track name=$@' > $@ && cat $< >> $@

%_intersect_f.raw: %_sites_start_f.raw %_pas_start_f.raw
	bedtools intersect -a $< -b $(word 2, $^) > $@

%_intersect_r.raw: %_sites_start_r.raw %_pas_start_r.raw
	bedtools intersect -a $< -b $(word 2, $^) > $@

%_start_f.raw: %_f.raw
	sed 's/\([^\t]*\)\t\([^\t]*\)\t.*/\1\t\2\t\2/' $< > $@

%_start_r.raw: %_r.raw
	sed 's/\([^\t]*\)\t[^\t]*\t\([^\t]*\).*/\1\t\2\t\2/' $< > $@

%_sites_f.raw: $(REFERENCE)
	fastools famotif2bed $< $@ $(MOTIF_F)

%_sites_r.raw: $(REFERENCE)
	fastools famotif2bed $< $@ $(MOTIF_R)

%_pas_f.raw: %_PAS.bed $(SIZES)
	bedtools slop -i $< -g $(word 2, $^) -l 1 -r 0 | grep '+' | cut -f -3 > $@

%_pas_r.raw: %_PAS.bed $(SIZES)
	bedtools slop -i $< -g $(word 2, $^) -l 1 -r 0 | grep '-' | cut -f -3 > $@

%_PAS.bed: $(ANNOTATION)
	zgrep $(FILTER) $(ANNOTATION) | cut -f 1,4,5,7 > $@
