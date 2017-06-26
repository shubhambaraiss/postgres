# Test for predicate locking in hash index
#
# Test to verify serialization failures
#
# Queries are written in such a way that an index scan(from one transaction) and an index insert(from another transaction) will try to access the same bucket of the index.


setup
{
 create table hash_tbl as select g*10+i id, g*10 p
 from  generate_series(1,4)g, generate_series(1,10)i;
 create index hash_pointidx on hash_tbl using hash(p);
}

teardown
{
 DROP TABLE hash_tbl;
}


session "s1"
setup		{ 
		  BEGIN ISOLATION LEVEL SERIALIZABLE;
		  set enable_seqscan=off;
		  set enable_bitmapscan=off;
		  set enable_indexonlyscan=on;
		}
step "rxy1"	{ select sum(p) from hash_tbl where p=20; }
step "wx1"	{ insert into hash_tbl (id, p)
                  select g, 30 from generate_series(51, 60) g; }
step "c1"	{ commit; }


session "s2"
setup		{ 
		  BEGIN ISOLATION LEVEL SERIALIZABLE;
		  set enable_seqscan=off;
		  set enable_bitmapscan=off;
		  set enable_indexonlyscan=on;
		}
step "rxy2"	{ select sum(p) from hash_tbl where p=30; }
step "wy2"	{ insert into hash_tbl (id, p)
                  select g, 20 from generate_series(61, 70) g; }
step "c2"	{ commit; }
