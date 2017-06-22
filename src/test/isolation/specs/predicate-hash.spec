# Test for predicate locking in hash index
#
# Test to verify serialization failures
#
# Queries are written in such a way that an index scan(from one transaction) and an index insert(from another transaction) will try to access the same bucket of the index.


setup
{
 create table hash_point_tbl(id int4, p integer);
 create index hash_pointidx on hash_point_tbl using hash(p);
 insert into hash_point_tbl (id, p)
 select g, 10 from generate_series(1, 10) g;
 insert into hash_point_tbl (id, p)
 select g, 20 from generate_series(11, 20) g;
 insert into hash_point_tbl (id, p)
 select g, 30 from generate_series(21, 30) g;
 insert into hash_point_tbl (id, p)
 select g, 40 from generate_series(31, 40) g;
}

teardown
{
 DROP TABLE hash_point_tbl;
}


session "s1"
setup		{ 
		  BEGIN ISOLATION LEVEL SERIALIZABLE;
		  set enable_seqscan=off;
		  set enable_bitmapscan=off;
		  set enable_indexonlyscan=on;
		}
step "rxy1"	{ select sum(p) from hash_point_tbl where p=20; }
step "wx1"	{ insert into hash_point_tbl (id, p)
                  select g, 30 from generate_series(41, 50) g; }
step "c1"	{ commit; }


session "s2"
setup		{ 
		  BEGIN ISOLATION LEVEL SERIALIZABLE;
		  set enable_seqscan=off;
		  set enable_bitmapscan=off;
		  set enable_indexonlyscan=on;
		}
step "rxy2"	{ select sum(p) from hash_point_tbl where p=30; }
step "wy2"	{ insert into hash_point_tbl (id, p)
                  select g, 20 from generate_series(51, 60) g; }
step "c2"	{ commit; }
