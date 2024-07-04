# import openpyxl
#
# # Step 3: XML 결과 파싱
# tree = ET.parse('result.xml')
# root = tree.getroot()
#
# # 테스트 결과 추출
# tests = int(root.attrib['test'])
# errors = int(root.attrib['errors'])
# failures = int(root.attrib['failures'])
# skipped = int(root.attrib['skipped'])
# passed = tests - errors - failures - skipped
#
# # 엑셀 파일 로드
# wb = openpyxl.load_workbook('/test/Test_Report.xlsx')  # 엑셀 파일 경로
# sheet = wb.active
#
# # Step 4: 엑셀 파일 업데이트
# sheet['C5'] = passed  # PASSED
# sheet['C6'] = failures  # FAILED
# sheet['C7'] = tests  # (total) Tests executed
#
# # 엑셀 파일 저장
# wb.save('/test/updated_test_report.xlsx')
#
#
# # pytest --junitxml=result.xml