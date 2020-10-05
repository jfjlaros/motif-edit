#
# Configuration.
#

# Motifs (forward and reverse complement).
MOTIF_F := 'A[AT]TAAA.{12,17}GG'
MOTIF_R := 'CC.{12,17}TTTA[TA]T'

# Reference data.
BUILD := hg38
REFERENCE := $(BUILD).fa
SIZES := $(BUILD).chrom.sizes
ANNOTATION := gencode.v35.polyAs.gff3.gz
FILTER := 'polyA_signal'

# Reference data sources.
REFERENCE_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(REFERENCE).gz
SIZES_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(SIZES)
ANNOTATION_URL := ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_35/$(ANNOTATION)

# Analysis tools.
BEDTOOLS := bedtools
FASTOOLS := fastools

# Output files.
OUT := intersect # sites sites_start ann ann_start


#
# Output preparation.
#

OUT_FILES := \
  $(foreach O, $(OUT), \
    $(foreach S, f r, \
      $(addprefix $(BUILD)_, \
        $(addsuffix _$S.bed, $O))))


#
# Maintenance targets.
#

.PHONY: all clean distclean features reference

all: $(OUT_FILES)

clean:
	rm -f $(OUT_FILES)

distclean: clean
	rm -f $(REFERENCE) $(SIZES) $(ANNOTATION)

# Features that can be used in the `FILTER` variable.
features: $(ANNOTATION)
	@zgrep -v '^#' $(ANNOTATION) | cut -f 3 | sort -u

# Location of reference data.
reference:
	@echo "$(REFERENCE_URL)\n$(SIZES_URL)\n$(ANNOTATION_URL)"


#
# Reference data download targets.
#

$(REFERENCE):
	wget $(REFERENCE_URL) && gunzip $@.gz

$(SIZES):
	wget $(SIZES_URL)

$(ANNOTATION):
	wget $(ANNOTATION_URL)


#
# Analysis targets.
#

# Add a header to a BED file.
%.bed: %.raw
	echo 'track name=$@' > $@ && cat $< >> $@

# Intersect motif sites and annotation (forward strand).
%_intersect_f.raw: %_sites_start_f.raw %_ann_start_f.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

# Intersect motif sites and annotation (reverse strand).
%_intersect_r.raw: %_sites_start_r.raw %_ann_start_r.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

# Convert a region to a start position (forward strand) by using column 2 twice.
%_start_f.raw: %_f.raw
	sed 's/\([^\t]*\)\t\([^\t]*\)\t.*/\1\t\2\t\2/' $< > $@

# Convert a region to a start position (reverse strand) by using column 3 twice.
%_start_r.raw: %_r.raw
	sed 's/\([^\t]*\)\t[^\t]*\t\([^\t]*\).*/\1\t\2\t\2/' $< > $@

# Find motif sites (forward strand).
%_sites_f.raw: $(REFERENCE)
	$(FASTOOLS) famotif2bed $< $@ $(MOTIF_F)

# Find motif sites (reverse strand).
%_sites_r.raw: $(REFERENCE)
	$(FASTOOLS) famotif2bed $< $@ $(MOTIF_R)

# Convert GFF3 regions to BED regions (off by one start position fix, forward strand).
%_ann_f.raw: %_ann.bed $(SIZES)
	$(BEDTOOLS) slop -i $< -g $(word 2, $^) -l 1 -r 0 | grep '+' | cut -f -3 > $@

# Convert GFF3 regions to BED regions (off by one start position fix, reverse strand).
%_ann_r.raw: %_ann.bed $(SIZES)
	$(BEDTOOLS) slop -i $< -g $(word 2, $^) -l 1 -r 0 | grep '-' | cut -f -3 > $@

# Filter the annotation file.
%_ann.bed: $(ANNOTATION)
	zgrep $(FILTER) $(ANNOTATION) | cut -f 1,4,5,7 > $@
