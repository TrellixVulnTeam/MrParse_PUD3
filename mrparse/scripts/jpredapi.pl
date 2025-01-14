#!/usr/bin/env perl 
use strict;
use warnings;

# Author: Alexey Drozdetskiy 
# Email: a.drozdetskiy@dundee.ac.uk
# ---
# Dr. Alexey Drozdetskiy
# Senior Postdoctoral Research Assistant
# The Barton Group
# Division of Computational Biology
# College of Life Sciences
# University of Dundee, DD1 5EH, Dundee, Scotland, UK.
# Tel:+44 1382 88731
# www.compbio.dundee.ac.uk
# The University of Dundee is registered Scottish charity: No.SC015096

# Please contact me with suggestions to improve/fix client/server part of the JPred API. 
# Do not assume it's OK to modify the API and to try your version on live JPred installation. 
# Users abusing JPred servers effectively preventing others from using the service will be banned.

# For documentation: run jpredapi without arguments like so: 'perl jpredapi'
# JPred API tutorial is available at: http://www.compbio.dundee.ac.uk/jpred4/api.shtml

use constant JPRED4  => 'http://www.compbio.dundee.ac.uk/jpred4';
use constant HOST    => 'http://www.compbio.dundee.ac.uk/jpred4/cgi-bin/rest';
use constant VERSION => 'v.1.5';

use HTTP::Request;
use HTTP::Request::Common;
use LWP::UserAgent;

# A handy shortcut for building a quick-and-dirty command-line interface
sub subcommand($$) {
    my ($expected, $code) = @_;
    if ($expected eq $ARGV[0]) {
        shift @ARGV;
        $code->();
        exit;
    }
}

# A shortcut for outputting errors
sub barf($) {
    my $response = shift;
    my ($message) = $response->content =~ m{<p>([^<]+)</p>};
    die "ERROR: $message\n";
}

my $ua = LWP::UserAgent->new;

my $minInterval = 10; # IMPORTANT: please don't decrease this constant. Users abusing JPred server will be banned.

my $checkVersion = $ua->request(GET HOST.'/version');
if ($checkVersion->is_success) {
    #print $checkVersion->content;
    if ($checkVersion->content =~ /VERSION=(v\.[0-9]*.[0-9]*)/) {
	if ($1 ne VERSION) {
	    print "\n\n\n********************************* WARNING: *********************************\n";
	    print "\nThe jpredapi script version is out of date.\nPlease download the up to date version at the following link:\nhttp://www.compbio.dundee.ac.uk/jpred4/downloads/jpredapi.tar.gz\n";
	    print "\nPausing for 20 sec to allow you to read the warning.\n";
	    print "\n****************************************************************************\n\n\n";
	    sleep(20);
	}
    }
}


if ($#ARGV == -1 || $ARGV[0] eq '-h' || $ARGV[0] eq 'help' || ($ARGV[0] ne 'status' && $ARGV[0] ne 'submit' && $ARGV[0] ne 'quota' && $ARGV[0] ne 'sectonewday')) {
    doc();
    exit();
}

sub doc {
    my $doc = <<END;

    JPred RESTful API client v.1.5 documentation.

    General: 
	please note that jobs run through this client program will be submitted to the JPred 4 server:
        http://www.compbio.dundee.ac.uk/jpred4

    A tutorial about the JPred API is available at:
        http://www.compbio.dundee.ac.uk/jpred4/api.shtml

    Email: 
	Usage of your email address is optional on single sequence job submission, but if you use one  - you will be
	notified when the job is complete or sent some diagnostics if it crashed. Email is obligatory for batch job submission. 
	Results from batch submissions are sent by email and link to individual job results and to an archive containing ALL results.
	If you use email for your submissions we may ocassionaly contact you about major updates to the JPred server and JPred API.

    ========== COMMANDS ==========

  1.
    To print this documentation run jpredapi without arguments like so:
       'perl jpredapi'


  2.
    To submit a JPred job do:	
       'perl jpredapi submit file=filename mode=batch format=fasta email=name\@domain.com name=my_test_job skipPDB=on'
    or
       'perl jpredapi submit mode=single format=raw email=name\@domain.com name=my_test_job skipPDB=on seq=MQVWPIEGIKKFETLSYLPPLTVEDLLKQIEYLLRSKWVPCLEFSKVGFVYRENHRSPGYYDGRYWTMWKLPMFGCTDATQVLKELEEAKKAYPDAFVRIIGFDNVRQVQLISFIAYKPPGC'
    where:
       'file=filename' - filename is the name of a file with the job input, see example_submission_sequence.txt (file name/suffix could be any, e.g. it does not have to be something like name.fasta for FASTA format file)
       'seq=AAAABBB' - instead of passing input file, for one-sequence submission you can submit jobs with sequences passed right through command line
       'format=batch' - defines format. Possible values are: 
          - batch (multiple sequence submission, file in FASTA format)
          - seq (single sequence submission in raw/FASTA format)
          - or multiple sequence submission formats: msf, blc, fasta
       'email=name\@domain.com' - defines email address where job report will be sent (optional for all but batch submissions). We DO recommend to use email.
       'name=my_test_job_number_3' - defines (optional) job name
       'skipPDB=on' - possible values are: on and off. If on - PDB check will not be performed - this is default for JPred API (see JPred documentation for more details on PDB check). Since default is defined, parameter is optional.
    
    NOTE: 
       order of parameters is not important, optional parameters could be left out.
    NOTE: 
       adding the word 'silent' to the command line will suppress all but essential output, e.g.:
       'perl jpredapi submit file=filename mode=batch format=fasta email=name\@domain.com name=my_test_job skipPDB=on silent'
  
  2.1 
    Check submission_all_types_example.csh script file provided for further examples.

  2.2
    Check *.example files for example of inputs in all valid combinations of mode/format: batch_fasta.example, msa_blc.example, msa_fasta.example, msa_msf.example, single_fasta.example, single_raw.example

  2.2.1 
    Valid combinations of mode/format are: mode=single format=raw, mode=single format=fasta, mode=msa format=fasta, mode=msa format=msf, mode=msa format=blc, mode=batch format=fasta
 

  3.
    To check JPred job status do:
       'perl jpredapi status jobid=id [getResults=yes] [checkEvery=60] [silent]'
    where:
       'job=jobid' - jobid is JPred job id returned on submission
       'getResults=yes' - if job successful jpredapi will download job results archive when ready (it is default, so, parameter could be left out)
       'checkEvery=60' - how often to check for job status in seconds (default 60 seconds = 1 min, minimum is 10 seconds) - it is optional parameter, you may leave it out, script will take care of it
                       NOTE: if using 'checkEvery=once' the program will perform status check just once and exit
       'silent' - adding the word 'silent' to the command line will suppress all but essential output

  3.1      
    Check one_job_retrieval.csh script file provided. One can use it to retrieve JPred job results like so:
       'source one_job_retrieval.csh jobId' - where jobId is the JPred job id returned at submission (id looks like: jp_OpHCA0J)


  4.
    To check how many jobs you have already submitted on a given day (out of 1000 maximum allowed jobs per user per day) do:
        'perl jpredapi quota email=name\@domain.com'
    where: 
	'email=name\@domain.com' - defines email address you use for job submissions

  5.
    To check how much time (in sec) left before more jobs are allowed from a given user (limit is 1000 jobs per user per day) do:
        'perl jpredapi sectonewday'

END
    print $doc;
}



my $silent = 0;
subcommand 'submit' => sub {
    my ($file,$mode,$format,$skipPDB,$email,$name,$seq) = ('defaultNotDefined','defaultNotDefined','defaultNotDefined','on','defaultNotDefined','defaultNotDefined','defaultNotDefined'); 
    my $paramsLine = '';
    my $delim = '£€£€';
    my $n = scalar @ARGV;
    
    my $formatUser;
    for (my $i=0; $i<$n; $i++) {
	my $a = $ARGV[$i];
	if ($a =~ /^(.*)=(.*)$/) {
	    my $key=$1;
	    my $val=$2;
	    if ($key eq 'file') {$file = $val;}
	    if ($key eq 'mode') {$mode = $val;}
	    if ($key eq 'format') {$formatUser = $val;}# $paramsLine = $paramsLine.$a.$delim;}
	    if ($key eq 'skipPDB') {$skipPDB = $val; $paramsLine = $paramsLine.$a.$delim;}
	    if ($key eq 'email') {$email = $val; $paramsLine = $paramsLine.$a.$delim;}
	    if ($key eq 'name') {$name = $val; $paramsLine = $paramsLine.$a.$delim;}
	    if ($key eq 'seq') {$seq = $val;}	    
	}
	if ($a eq 'silent') {$silent=1;}
    }     
    if (!($paramsLine =~ /skipPDB/)){$paramsLine = $paramsLine.'skipPDB='.$skipPDB.$delim;}
    if ( ($formatUser eq 'raw' && $mode eq 'single') 
	 || ($formatUser eq 'fasta' && $mode eq 'single') 
	 || ($formatUser eq 'fasta' && $mode eq 'msa') 
	 || ($formatUser eq 'msf' && $mode eq 'msa') 
	 || ($formatUser eq 'blc' && $mode eq 'msa') 
	 || ($formatUser eq 'fasta' && $mode eq 'batch') 
	) {
	if ($formatUser eq 'raw' && $mode eq 'single') {$format = 'seq';}
	if ($formatUser eq 'fasta' && $mode eq 'single') {$format = 'seq';}
	if ($formatUser eq 'fasta' && $mode eq 'msa') {$format = 'fasta';}
	if ($formatUser eq 'msf' && $mode eq 'msa') {$format = 'msf';}
	if ($formatUser eq 'blc' && $mode eq 'msa') {$format = 'blc';}
	if ($formatUser eq 'fasta' && $mode eq 'batch') {$format = 'batch';}
	$paramsLine = $paramsLine.'format='.$format.$delim;
    } else {
	print "ERROR: Invalid mode/format combination. Valid combinations are:\nmode=single format=raw\nmode=single format=fasta\nmode=msa format=fasta\nmode=msa format=msf\nmode=msa format=blc\nmode=batch format=fasta\n...Exiting.\n";
        exit();
    }
    if ($file eq 'defaultNotDefined' && $seq eq 'defaultNotDefined') {
	print "ERROR: Neither input sequence nor input file defined. Exiting.\n";
	exit();
    }
    if ($file ne 'defaultNotDefined' && $seq ne 'defaultNotDefined') {
        print "ERROR: Both input file and sequence defined. Please choose one or the other. Exiting.\n";
        exit();
    }
    if ($seq ne 'defaultNotDefined' && $format ne 'seq') {
        print "ERROR: when sequence is defined like so 'seq=AABBCC' format has to be 'seq'. Exiting.\n";
        exit();
    }
    if ($email eq 'defaultNotDefined') {
	if (!$silent) {print "NOTE: email is not defined. Please consider using email for next submission (see documentation for details on why using email).\n";}
    }
    if ($email eq 'defaultNotDefined' && $format eq 'batch') {
	print "ERROR: when submitting batch job email is obligatory (you will receive detailed report, list of links and a link to archive to all results via email. Exiting.\n)";
	exit();
    }
    if ( !($skipPDB eq 'on' || $skipPDB eq 'off') ) {
	print "ERROR: skipPDB parameter values could only be 'on' (skip PDB check, default) or 'off' (perform PDB check). Exiting.\n";
	exit();
    } 
    if ( !($name =~ /^\w+$/) ) {
	print "ERROR: name parameter could only be built from Latin characters, numbers, and '_' symbol. Exiting.\n";
	exit();
    }

    if (!$silent) {
	print "Your job will be submitted with the following parameters:\n";
	if ($file ne 'defaultNotDefined') {print "file: $file\n";}
	if ($seq ne 'defaultNotDefined') {print "seq: $seq\n";}
	print "format: $format\n";
	print "skipPDB: $skipPDB\n";
	if ($email ne 'defaultNotDefined') {print "email: $email\n";}
	if ($name ne 'defaultNotDefined') {print "name: $name\n";}
	#print ": $\n";
    }

    my $resource;
    if ($file ne 'defaultNotDefined') {
	open( INPUT, $file) or die "ERROR:\tFile $file does not exist.\n";
	while ( my $line = <INPUT> ) {
	    $resource .= $line;
	}
	close(INPUT);
    }
    if ($seq ne 'defaultNotDefined') {
	$resource .= ">query\n".$seq;
    }
    $resource = $paramsLine.$resource;

    #print "RESOURCE:\n$resource\n";

    my $response = $ua->request(POST HOST.'/job', 
				'Content-Type' => 'text/txt',
				Content        => $resource
	);
    # On success
    if ($response->is_success) {
	if ($format ne 'batch') {
	    my $url;	
	    $url = $response->header('Location');
	    my ($id) = $url =~ /(jp_.*)$/;
	    if ($id) {
		if (!$silent) {
		    print "\n\nCreated JPred job with jobid: $id\n";
		    print "You can check the status of the job using the following URL: $url\n";
		    print "...or using 'perl jpredapi status jobid=$id getResults=yes checkEvery=60 silent' command\n";
		    print "(Check documentation for more details.)\n";
		} else {
		    print "Created JPred job with jobid: $id\n";
		}
	    } else {
		print "\n\nERROR: ";
		print $response->content;
		print "\n\n";
	    }
	} 
	if ($format eq 'batch') {
	    my $message = $response->content;# =~ m{<h1>([^<]+)</h1>};
	    $message =~ s/^<h1>\s+|<\/h1>$//g;
	    print "$message\n";
	}
    }
    # On failure, barf
    else {
        barf $response;
    }

};






#perl jpredapi status jobid=id [getResults=yes] [checkEvery=60] [silent]
subcommand 'status' => sub {
    my ($id,$interval,$getResults,$silent) = ('defaultNotDefined',60,'yes',0);
    my $n = scalar @ARGV;
        
    for (my $i=0; $i<$n; $i++) {
	my $a = $ARGV[$i];
	if ($a =~ /^(.*)=(.*)$/) {
	    my $key=$1;
	    my $val=$2;
	    if ($key eq 'jobid') {$id = $val;}
	    if ($key eq 'getResults') {$getResults = $val;}
	    if ($key eq 'checkEvery') {$interval = $val;}
	}
	if ($a eq 'silent') {$silent=1;}
    }     

    if (!$silent) {
	print "Your job status will be checked with the following parameters:\n";
	print "JobId: $id\n";
	print "getResults: $getResults\n";
	print "checkEvery: $interval [sec]\n";
    }

    my $jobDoneFlag = 0;
    my $jobDoneFlagExtra = 0;
    do {
	my $now_string = localtime;
	print "$now_string\t--->\t";
	my $response = $ua->request(GET HOST.'/job/id/'.$id);
	# On success
	if ($response->is_success) {
	    print $response->content;
	    print "\n";

	    if ($response->content =~ /finished/) {
		if ($getResults eq "yes") {
		    if (!$silent) {print "Will attempt to download results now (using 'curl') from:\n";}
		    my $arcURL = JPRED4."/results/$id/$id.tar.gz";
		    if (!$silent) {print "$arcURL\n\n";}
		    system("mkdir $id");
			system("curl -o $id.tar.gz $arcURL");
		    system("mv $id.tar.gz $id/.");
		    print "Job results archive is now available at: $id/$id.tar.gz\n";
		}
		$jobDoneFlag = 1;
	    }
	    if ($response->content =~ /malformed/) {$jobDoneFlag = 1;}
	    if ($response->content =~ /does not exist in the queue/) {$jobDoneFlag = 1;}
	    if ($response->content =~ /No job of that ID/) {$jobDoneFlagExtra++;}
	    if ($jobDoneFlagExtra > 2) {$jobDoneFlag = 1;}
	    #if ($response->content =~ //) {$jobDoneFlag = 1;}
	}
	# On failure, barf
	else {
	    barf $response;
	    $jobDoneFlag = 1;
	}
	if ($jobDoneFlag || $interval eq 'once') {exit();}
	sleep($interval);
    } while (!($jobDoneFlag));

};








subcommand 'quota' => sub {
    my $n = scalar @ARGV;
    my $email;
    for (my $i=0; $i<$n; $i++) {
	my $a = $ARGV[$i];
	if ($a =~ /^(.*)=(.*)$/) {
	    my $key=$1;
	    my $val=$2;
	    if ($key eq 'email') {$email = $val;}
	}
    }     
    
    my $response = $ua->request(GET HOST.'/quota/'.$email);
    if ($response->is_success) {
	print $response->content;
    }
};








subcommand 'sectonewday' => sub {
    my $response = $ua->request(GET HOST.'/sectonewday');
    if ($response->is_success) {
        print $response->content;
    }
};

