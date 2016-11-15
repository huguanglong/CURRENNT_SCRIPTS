#!/usr/bin/perl
###############################################################
## General Description:
##		This script prepares the test data
## Usage:
##		Step: 
##		 . Prepare the list of input features in advance
##		   Prepare the data_config.py in $prjdir for testset
##		1. Acquire the timesteps and dimensions of the data,
##		   generate $prjdir/all.scp
##		2. Generate the .nc file for test set
##		3. Normalize the data and put the mean, std into the
##		   .nc file
## Notes:
##		1. If the same testset is used for several systems,
##			no need to re-generate scp (step $FLAG_SCP). But nc
##			file must be re-generated (step $PREP_DAT)
##		2. Please configure data_config.py before running
###############################################################

use Cwd;
use File::Basename;

# data dir
$prjdir    = $ARGV[0]; 
# mean and variance 
$datamv    = $ARGV[1]; 
# buff dir
$buffdir   = $ARGV[2];

require($ARGV[3]) || die "Can't not load $ARGV[3]";

if ($ARGV[4] > 0){
    print "DEBUG mode\n";
    $DEBUG = 1;
}


## reserved options
$RAND_SCP  = 0;			
$flagMultiNC = 1;		

mkdir $buffdir;
if ($RAND_SCP){
	print "This is the script for test set, no need to generate randomized list\n";
	print "Please write the list of input files to scp in inScpFile of data_config.py\n";
	print "Example:\n\t lab.scp:\n\t/home/path/1.lab\n\t/home/path/2.lab\n\t...\n";
	
	#print "Found the randomized list in $randomDir\n";
	# generate .scp
	#opendir($D, $randomDir) || die "can't open $randomDir";
	#@files = readdir($D);
	#@files = grep {/[\S]+.scp/} @files;
	#closedir(D);

	#foreach $file (@files){
	#	system("echo $file");
	#	$filename = $file;
	#	$filename =~ s/\_r\_full//g;
	#	SelfSystem("cat $randomDir/$file | head -n $numUtt > $prjdir/$filename");
	#}	
}

if ($TEST_FLAG_SCP){
    # Delete the old *.info if new .scp is utilized
    SelfSystem("rm $prjdir/*.info");
    if(-e "$prjdir/data_config.py"){
    }else{
	print "Can't find $prjdir/data_config.py";
	die "Please use ./template/data_config.py_test as template\n";
    }
    # prepare to list for packaging data
    SelfSystem("python ./utilities/PrePareData.py $prjdir/data_config.py $prjdir");
    # generate a new gen.scp
    
    if (-e "$prjdir/all.scp"){
    }else{
	die "Fail to generate $prjdir/all.scp\n";
    }

    $scpFile = "$prjdir/all.scp";
    $dataScp = "$prjdir/gen.scp";
    open(IN_STR, "$scpFile");
    open(OUT_STR,">$dataScp");
    $count=1;
    while(<IN_STR>){
	chomp();
	$file = $_;
	open(IN_STR_2, "$file");
	while(<IN_STR_2>){
	    chomp();
	    @lineContents = split(' ', $_);
	    print OUT_STR "$lineContents[5]\n";
	}
	close(IN_STR_2);
    }
    close(OUT_STR);
    close(IN_STR);
    print "$prjdir/all.scp ad $prjdir/gen.scp have beeen generated\n";
}


if ($TEST_PREP_DAT){
    if (-e "$prjdir/mask.txt"){
	print "Using the mask file $prjdir/mask.txt\n";
	$maskfile = "$prjdir/mask.txt";
    }else{
	$maskfile = "";
    }
    if ( -e "$prjdir/normMask" ) {
        print "Using the normMask $prjdir/normMask\n";
        $normMaskBin = "$prjdir/normMask";
    }
    else {
        $normMaskBin = "";
        print "Not using norm mask";
    }
    if ( -e "$prjdir/normMethod") {
	print "Using the normMethod $prjdir/normMethod\n";
	$normMethod = "$prjdir/normMethod";
    }else{
	$normMethod = "None";
	print "Not using norm method\n";
    }
    if (-e "$prjdir/all.scp"){
    }else{
	die "Can't find all.scp";
    }
    if ($dataPack ne ""){
	$command = "python ./utilities/PackData.py $prjdir/all.scp $datamv";
	$command = "$command $buffdir 1 0 1";
	system("mkdir -p $buffdir");
	# add mask
	if ($maskfile ne ""){
	    $command = "$command $maskfile";
	}else{
	    $command = "$command None";
	}
	# add mean and variance
	$command = "$command 1";
	if ($normMaskBin ne ""){
	    $command = "$command $normMaskBin";
	}else{
	    $command = "$command None";
	}
	if ($normMethod ne ""){
	    $command = "$command $normMethod";
	}else{
	    $command = "$command None";
	}

	SelfSystem($command);

    }else{
	if ($flagMultiNC){
	    $scpFile = "$prjdir/all.scp";
	    $dataScp = "$prjdir/data.scp";
	    open(IN_STR, "$scpFile");
	    open(OUT_STR,">$dataScp");
	    $count=1;
	    while(<IN_STR>){
		chomp();
		$file = $_;
		$name = basename($file);
		$name =~ s/all.scp/data.nc/g;
		$commandline = "$bmat2nc $file $buffdir/$name";
		if ($maskfile eq ""){
		    
		}else{
		    $commandline = "$commandline $maskfile";
		}
		SelfSystem($commandline);			
		print OUT_STR "$buffdir/$name\n";
	    
		$commandline = "$ncnorm $buffdir/$name $datamv + +";
		print "\n**** Normalizing $name\n";
		SelfSystem($commandline);
		$count = $count + 1;
	    }
	    close(IN_STR);
	    close(OUT_STR);		
	}
    }
}

