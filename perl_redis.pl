#!/usr/bin/perl -w

use strict;
use warnings;
use Redis;
use Try::Tiny;

my $r = Redis->new (server => '127.0.0.1:6379', encoding => 'utf-8')
        || die "Redis connection failed";

$r->set('aa' => '11');

# Test
# $r->ping || die "Ping failed. No server?";

my $value = $r->get('aa');
print "$value\n";

my $i = 0;
while(1){
    $i++;
    eval{
        $r->set('aa' => $i);
        $value = $r->get('aa');
        print "$value\n";
    };

    if($@){
	warn "caught error: $@";
        #TODO:reconnect
	last;	
    };
}


$r->quit;
