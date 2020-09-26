# workon fastools

MOTIF_F := 'A[AGT]TAAA.{12,17}GG'
MOTIF_R := 'CC.{12,17}TTTA[TCA]T'
BUILD := hg38
OUT := sites sites_start pas pas_start intersect

REFERENCE := input/$(BUILD).fa
SIZES := input/$(BUILD).chrom.sizes
PAS := input/hg38_PAS.bed
STRAND := f r


OUT_FILES := \
  $(foreach O, $(OUT), \
    $(foreach S, $(STRAND), \
      $(addprefix $(BUILD)_, \
        $(addsuffix _$S.bed, $O))))


all: $(OUT_FILES)

clean:
	rm -f $(OUT_FILES)

%.bed: %.raw
	echo 'track name=$@' > $@ && cat $< >> $@

%_start_f.raw: %_f.raw
	sed 's/\([^\t]*\)\t\([^\t]*\)\t.*/\1\t\2\t\2/' $< > $@

%_start_r.raw: %_r.raw
	sed 's/\([^\t]*\)\t[^\t]*\t\([^\t]*\).*/\1\t\2\t\2/' $< > $@

%_sites_f.raw: $(REFERENCE)
	fastools famotif2bed $< $@ $(MOTIF_F)

%_sites_r.raw: $(REFERENCE)
	fastools famotif2bed $< $@ $(MOTIF_R)

%_pas_f.raw: $(PAS) $(SIZES)
	bedtools slop -i $< -g $(word 2, $^) -l 1 -r 0 | grep '+' | cut -f -3 > $@

%_pas_r.raw: $(PAS) $(SIZES)
	bedtools slop -i $< -g $(word 2, $^) -l 1 -r 0 | grep '-' | cut -f -3 > $@

%_intersect_f.raw: %_sites_start_f.raw %_pas_start_f.raw
	bedtools intersect -a $< -b $(word 2, $^) > $@

%_intersect_r.raw: %_sites_start_r.raw %_pas_start_r.raw
	bedtools intersect -a $< -b $(word 2, $^) > $@
