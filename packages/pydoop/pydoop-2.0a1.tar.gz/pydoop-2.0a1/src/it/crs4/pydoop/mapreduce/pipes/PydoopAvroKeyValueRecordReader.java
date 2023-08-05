/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied.  See the License for the specific language governing
 * permissions and limitations under the License.
 */

package it.crs4.pydoop.mapreduce.pipes;

import java.io.IOException;

import org.apache.avro.Schema;
import org.apache.avro.generic.GenericRecord;


public class PydoopAvroKeyValueRecordReader
    extends PydoopAvroRecordReaderBase<GenericRecord, GenericRecord> {

  public PydoopAvroKeyValueRecordReader(Schema readerSchema) {
    super(readerSchema);
  }

  @Override
  public GenericRecord getCurrentKey()
      throws IOException, InterruptedException {
    return (GenericRecord) getCurrentRecord().get("key");
  }

  @Override
  public GenericRecord getCurrentValue()
      throws IOException, InterruptedException {
    return (GenericRecord) getCurrentRecord().get("value");
  }
}
