#!/usr/bin/perl -w

use strict;
use warnings;

use Redis::hiredis;
my $redis = Redis::hiredis->new();
$redis->connect('127.0.0.1', 6379);
$redis->command('set foo bar');
$redis->command(["set", "foo", "bar baz"]); # values with spaces
my $val = $redis->command('get foo');

# to pipeline commands
$redis->append_command('set abc 123');
$redis->append_command('get abc');
my $set_status = $redis->get_reply(); # 'OK'
my $get_val = $redis->get_reply(); # 123

print $set_status, $get_val;

my $r = $redis;

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
