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
SKIP_EXONS := python skip_exons.py
INTERSECT_GTF:= python intersect_gtf.py
GTF_TO_CSV:= python gtf_to_csv.py

#
# Maintenance targets.
#

.PHONY: all clean distclean reference gtf
.SECONDARY:

all: $(REFERENCE) $(GTF) editable_exons_G.csv
	 

clean:
	rm -f *.raw *.bed editable_exons_*

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
skip_exons.bed : $(GTF)
	$(SKIP_EXONS) --gtf $? > $@

# Find motif sites.
motif_%.raw: $(REFERENCE) $(MOTIFS)
	$(FASTOOLS) famotif2bed $< $@ '$(shell grep -- "^$*" $(MOTIFS) | cut -f 3)'

# Find splice sites that are editable
editable_exons_%.bed: skip_exons.bed motif_%.raw
	$(BEDTOOLS) intersect -a $< -b $(word 2, $^) > $@

editable_exons_%.gtf: editable_exons_%.bed $(GTF)
	$(INTERSECT_GTF) --bed $< --gtf $(word 2, $^) > $@

editable_exons_%.csv: editable_exons_%.gtf
	$(GTF_TO_CSV) --gtf $< > $@
