#
# Configuration.
#

# Reference data.
BUILD := hg38
GTF := Homo_sapiens.GRCh38.104.gtf
MOTIFS := motifs.tsv
REFERENCE := $(BUILD).fa

# Reference data sources.
GTF_URL := http://ftp.ensembl.org/pub/release-104/gtf/homo_sapiens/$(GTF).gz
REFERENCE_URL := https://hgdownload.cse.ucsc.edu/goldenPath/$(BUILD)/bigZips/$(REFERENCE).gz

# Analysis tools.
BEDTOOLS := bedtools
FASTOOLS := fastools
PARSE_GTF := python parse_gtf.py

#
# Maintenance targets.
#

.PHONY: all clean distclean reference gtf
.SECONDARY:

all: $(REFERENCE) $(GTF) splice.bed splice.tsv editable_splice_G.bed
	 

clean:
	rm -f *.mtf *.raw *.bed *.vcf splice.tsv

distclean: clean
	rm -f $(REFERENCE)


# Location of reference data.
reference:
	@echo "$(REFERENCE_URL)\n$(ANNOTATION_URL)"

#
# Reference data download targets.
#

$(REFERENCE):
	wget $(REFERENCE_URL) && gunzip $@.gz

$(GTF):
	wget $(GTF_URL) && gunzip $@.gz

#
# Analysis targets.
#

# Find the splice sites
splice.bed: $(GTF)
	$(PARSE_GTF) --gtf $? --bed splice.bed --tsv splice.tsv

splice.tsv: $(GTF)
	$(PARSE_GTF) --gtf $? --bed splice.bed --tsv splice.tsv

# Find motif sites.
motif_%.raw: $(REFERENCE) $(MOTIFS)
	$(FASTOOLS) famotif2bed $< $@ '$(shell grep -- "^$*" $(MOTIFS) | cut -f 3)'

# Find splice sites that are editable
editable_splice_%.bed: splice.bed motif_%.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@
