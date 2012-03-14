rm -rf rhmres00
mkdir rhmres00
rm -rf rhmres10
mkdir rhmres10
rm -rf rhmres20
mkdir rhmres20
rm -rf rhmres30
mkdir rhmres30
rm -rf rhmres40
mkdir rhmres40
rm -rf rhmres50
mkdir rhmres50
rm -rf rhmres60
mkdir rhmres60
rm -rf rhmres70
mkdir rhmres70
rm -rf rhmres80
mkdir rhmres80
rm -rf rhmres90
mkdir rhmres90


rm -rf rhmbk00
mkdir rhmbk00
rm -rf rhmbk10
mkdir rhmbk10
rm -rf rhmbk20
mkdir rhmbk20
rm -rf rhmbk30
mkdir rhmbk30
rm -rf rhmbk40
mkdir rhmbk40
rm -rf rhmbk50
mkdir rhmbk50
rm -rf rhmbk60
mkdir rhmbk60
rm -rf rhmbk70
mkdir rhmbk70
rm -rf rhmbk80
mkdir rhmbk80
rm -rf rhmbk90
mkdir rhmbk90

#_____________________00__________________________________________
resfolder=rhmres00
bkfolder=rhmbk00
echo '---------------------parzivalremain00----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain00separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done

#_____________________10__________________________________________
resfolder=rhmres10
bkfolder=rhmbk10
echo '---------------------parzivalremain10----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain10separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done

#_____________________20__________________________________________

resfolder=rhmres20
bkfolder=rhmbk20
echo '---------------------parzivalremain20----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain20separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________30__________________________________________
resfolder=rhmres30
bkfolder=rhmbk30
echo '---------------------parzivalremain30----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain30separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________40__________________________________________
resfolder=rhmres40
bkfolder=rhmbk40
echo '---------------------parzivalremain40----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain40separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________50__________________________________________
resfolder=rhmres50
bkfolder=rhmbk50
echo '---------------------parzivalremain50----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain50separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________60__________________________________________
resfolder=rhmres60
bkfolder=rhmbk60
echo '---------------------parzivalremain60----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain60separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________70__________________________________________
resfolder=rhmres70
bkfolder=rhmbk70
echo '---------------------parzivalremain70----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain70separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________80__________________________________________
resfolder=rhmres80
bkfolder=rhmbk80
echo '---------------------parzivalremain80----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain80separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done
#_____________________90__________________________________________
resfolder=rhmres90
bkfolder=rhmbk90
echo '---------------------parzivalremain90----------------------' | tee -a rhmnotrelog
for fn in 00 01 02 03 04 05 06 07 08 09 10; do
	date | tee -a rhmnotrelog
	./binarysankoff parzivalremain90separatefiles 25000 1
	./graph.sh
	date | tee -a rhmnotrelog
	
	mv sankoff-tree_0.dot rhm_dot1_$fn
	mv rhm_dot1_$fn $bkfolder
	mv sankoff-tree_noint.dot rhm_dot2_$fn
	mv rhm_dot2_$fn $bkfolder
	mv sankoff-tree.tre rhm_tre_$fn
	mv rhm_tre_$fn $resfolder
	mv dendro.dot rhm_dot3_$fn
	mv rhm_dot3_$fn $bkfolder
	mv dendro.ps rhm_ps1_$fn
	mv rhm_ps1_$fn $bkfolder
	mv sankoff-tree.pdf rhm_pdf_$fn
	mv rhm_pdf_$fn $bkfolder
	mv sankoff-tree.ps rhm_ps2_$fn
	mv rhm_ps2_$fn $bkfolder	
done

