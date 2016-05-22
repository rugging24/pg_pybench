#!/usr/bin/python

def getInitdbText() :
 return """ BEGIN; \
	DROP TABLE IF EXISTS testset;\
	CREATE TABLE testset( \
  	set serial PRIMARY KEY,\
  	config_info text not null,\
  	info text\
  	);\
	
	DROP TABLE IF EXISTS load_average ;\
	CREATE TABLE IF NOT EXISTS load_average(\
	set int NOT NULL REFERENCES testset(set) ON DELETE CASCADE,\
	repeat_number integer ,\
	scale integer,\
	load_1min numeric,\
	load_5min numeric, \
	load_15min numeric\
	);\

	DROP TABLE IF EXISTS disk_io_count ; \
	CREATE TABLE IF NOT EXISTS disk_io_count (\
	set int NOT NULL REFERENCES testset(set) ON DELETE CASCADE,\
	repeat_number integer ,\
	scale integer,\
	write_count numeric, \
	read_count numeric, \
	read_bytes numeric, \
	write_time numeric, \
	read_time  numeric \
	) ; \

	DROP TABLE IF EXISTS tests;\
	CREATE TABLE tests(\
  	test serial PRIMARY KEY,\
  	set int NOT NULL REFERENCES testset(set) ON DELETE CASCADE,\
  	scale int,\
  	dbsize int8,\
  	start_time timestamp default now(),\
  	end_time timestamp default null,\
  	tps decimal default 0,\
  	script text,\
  	clients int,\
  	workers int,\
  	trans int,\
  	avg_latency float,\
  	max_latency float,\
  	percentile_90_latency float,\
  	wal_written numeric,\
  	cleanup interval default null,\
  	rate_limit numeric default null\
  	);\

	DROP TABLE IF EXISTS timing;\
	-- Staging table, for loading in data from CSV\
	CREATE TABLE timing(\
  	ts timestamp,\
  	filenum int, \
  	latency numeric(9,3),\
  	test int NOT NULL REFERENCES tests(test)\
  	);\

	CREATE INDEX idx_timing_test on timing(test,ts);\

	DROP TABLE IF EXISTS test_bgwriter;\
	CREATE TABLE test_bgwriter(\
  	test int PRIMARY KEY REFERENCES tests(test) ON DELETE CASCADE,\
  	checkpoints_timed bigint,\
  	checkpoints_req bigint,\
  	buffers_checkpoint bigint,\
  	buffers_clean bigint,\
  	maxwritten_clean bigint,\
  	buffers_backend bigint,\
  	buffers_alloc bigint,\
  	buffers_backend_fsync bigint,\
  	max_dirty bigint\
	);\
	COMMIT;"""
