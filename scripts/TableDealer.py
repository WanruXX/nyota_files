import json
import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from lark_oapi.api.drive.v1 import *
import os


class TableDealer:
    
    def __init__(self, image_dir = "temp/", index = 0):
        self.image_dir = os.path.join(os.getcwd(), image_dir)
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        
        self.client = lark.Client.builder() \
            .enable_set_token(True) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()
            
        self.option = lark.RequestOption.builder().user_access_token(os.getenv("USER_ACCESS_TOKEN")).build()
        self.index = index
            
            
    def get_new_items(self, new_items_file, batch_size = 50):
        request: SearchAppTableRecordRequest = SearchAppTableRecordRequest.builder() \
            .app_token(os.getenv('APP_TOKEN')) \
            .table_id(os.getenv('TABLE_ID')) \
            .user_id_type("open_id") \
            .page_size(batch_size) \
            .request_body(SearchAppTableRecordRequestBody.builder()
                .view_id(os.getenv('VIEW_ID'))
                .field_names(["产品名字英文", "预览小图"])
                .filter(FilterInfo.builder()
                    .conjunction("and")
                    .conditions([Condition.builder()
                        .field_name("产品名字英文")
                        .operator("isNotEmpty")
                        .value([])
                        .build(), 
                        Condition.builder()
                        .field_name("预览小图")
                        .operator("isNotEmpty")
                        .value([])
                        .build(),
                        Condition.builder()
                        .field_name("产品描述英文")
                        .operator("isEmpty")
                        .value([])
                        .build()
                        ])
                    .build())
                .automatic_fields(False)
                .build()) \
            .build()

        response: SearchAppTableRecordResponse = self.client.bitable.v1.app_table_record.search(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        
        with open(new_items_file, 'w', encoding="utf-8") as file:
            file.write(lark.JSON.marshal(response.data, indent=4))
            self.index += 1
        
        
    def download_images(self, new_items_file):
        # item_iamges = {}
        with open(new_items_file, encoding="utf-8") as f:
            new_items = json.load(f)
            print("Loaded", new_items_file, "for downloading images")
            
        for item in new_items["items"]:
            fields = item["fields"]
            request: DownloadMediaRequest = DownloadMediaRequest.builder() \
                .file_token(fields["预览小图"][0]["file_token"]) \
                .build()

            response: DownloadMediaResponse = self.client.drive.v1.media.download(request, self.option)

            if not response.success():
                lark.logger.error(
                    f"client.drive.v1.media.download failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
                return
            
            image_filename = fields["产品名字英文"][0]["text"] + ".jpg"
            with open(os.path.join(self.image_dir, image_filename), 'wb') as file:
                file.write(response.file.read())
                file.close()
            # item_iamges[item.record_id] = image_filename
            print("Downloaded image ", image_filename)
    
    def update_descriptions(self, des_added_file):
        with open(des_added_file, encoding="utf-8") as f:
            des_added_items = json.load(f)
            print("Loaded", des_added_file, "for updating descriptions")
            
        records = []
        for item in des_added_items["items"]:
            records.append(AppTableRecord.builder()
                .fields({"产品描述英文": item["fields"]["产品描述英文"]})
                .record_id(item["record_id"])
                .build())
        
        request: BatchUpdateAppTableRecordRequest = BatchUpdateAppTableRecordRequest.builder() \
        .app_token(os.getenv('APP_TOKEN')) \
        .table_id(os.getenv('TABLE_ID')) \
        .request_body(BatchUpdateAppTableRecordRequestBody.builder()
            .records(records)
            .build()) \
        .build()

        response: BatchUpdateAppTableRecordResponse = self.client.bitable.v1.app_table_record.batch_update(request, self.option)

        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.batch_update failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

