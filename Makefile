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


#
# Maintenance targets.
#

.PHONY: all clean distclean features reference
.SECONDARY:

all: sum_a.bed sum_t.bed sum.bed

clean:
	rm -f *.raw *.bed

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

# Merge raw files.
sum.raw: sum_a.raw sum_t.raw
sum_a.raw: intersect_+f.raw intersect_-r.raw
sum_t.raw: intersect_+r.raw intersect_-f.raw

sum.raw sum_a.raw sum_t.raw:
	cat $^ | sort -k 1,1 -k 2,2n -u > $@

# Intersect motifs with annotation.
intersect_+f.raw: motif_+f.raw annotation_+.raw
intersect_-f.raw: motif_-f.raw annotation_-.raw
intersect_+r.raw: motif_+r.raw annotation_+.raw
intersect_-r.raw: motif_-r.raw annotation_-.raw

intersect_+f.raw intersect_-r.raw intersect_+r.raw intersect_-f.raw:
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

# Find motif sites.
motif_%.raw: $(REFERENCE) $(MOTIFS)
	$(FASTOOLS) famotif2bed $< $@ '$(shell grep -- $* $(MOTIFS) | cut -f 2)'

# Filter annotation and convert to zero based positions.
annotation_%.raw: $(ANNOTATION)
	grep '$(FILTER).*$*' $(ANNOTATION) | awk '{ print $$1"\t"($$4 - 1)"\t"($$4 - 1) }' > $@
