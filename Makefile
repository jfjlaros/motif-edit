#
# Configuration.
#

# Reference data.
BUILD := hg38
REFERENCE := $(BUILD).fa
MOTIFS := motifs.tsv
ANNOTATION := gencode.v35.polyAs.gff3
FILTER := polyA_signal

# Reference data sources.
REFERENCE_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(REFERENCE).gz
ANNOTATION_URL := ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_35/$(ANNOTATION).gz

# Analysis tools.
BEDTOOLS := bedtools
FASTOOLS := fastools

OUT_FILES := motif_+f.bed motif_-r.bed motif_+r.bed motif_-f.bed annotation_-.bed annotation_+.bed intersect_+f.bed intersect_-r.bed intersect_+r.bed intersect_-f.bed


#
# Maintenance targets.
#

.PHONY: all clean distclean features reference

all: $(OUT_FILES)

clean:
	rm -f $(OUT_FILES)

distclean: clean
	rm -f $(REFERENCE) $(ANNOTATION)

# Features that can be used in the `FILTER` variable.
features: $(ANNOTATION)
	@grep -v '^#' $(ANNOTATION) | cut -f 3 | sort -u

# Location of reference data.
reference:
	@echo "$(REFERENCE_URL)\n$(ANNOTATION_URL)"


#
# Reference data download targets.
#

$(REFERENCE):
	wget $(REFERENCE_URL) && gunzip $@.gz

$(ANNOTATION):
	wget $(ANNOTATION_URL) && gunzip $@.gz


#
# Analysis targets.
#

# Add a header to a BED file.
%.bed: %.raw
	echo 'track name=$*' > $@ && cat $< >> $@

# Intersect motifs and annotation (forward strand).
intersect_%f.raw: motif_%f.raw annotation_%.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

# Intersect motifs and annotation (reverse complement strand).
intersect_%r.raw: motif_%r.raw annotation_%.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

# Find motif sites.
motif_%.raw: $(REFERENCE) $(MOTIFS)
	$(FASTOOLS) famotif2bed $< $@ '$(shell grep -- $* $(MOTIFS) | cut -f 2)'

# Filter annotation and convert to zero based positions.
annotation_%.raw: $(ANNOTATION)
	grep '$(FILTER).*$*' $(ANNOTATION) | awk '{ print $$1"\t"($$4 - 1)"\t"($$4 - 1) }' > $@
