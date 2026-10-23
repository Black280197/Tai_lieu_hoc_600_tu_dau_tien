param([string]$File)

$pats = [ordered]@{
  'Dong'        = '.'
  'H3'          = '^### '
  'SotEND'      = 'END_OF_PART'
  'Img'         = '<img '
  'Img60'       = 'max-width: 60%'
  'NoiTich'     = 'nội tích'
  'NoiTai'      = 'nội tại'
  'Pinyin'      = '^\* \*\*Pinyin:\*\*'
  'HanViet'     = '^\* \*\*Hán Việt:\*\*'
  'Nghia'       = '^\* \*\*Nghĩa:\*\*'
  'BoThu'       = '^\* \*\*Bộ thủ:\*\*'
  'PhanLoai'    = '^\* \*\*Phân loại từ:\*\*'
  'NetVe'       = '^\*\*Nét vẽ chữ'
  'BocTach'     = '^\*\*Bóc tách thành phần từng chữ\*\*'
  'NguonGocChu' = '^\*\*Nguồn gốc & Bản chất từng chữ\*\*'
  'NguonGocTu'  = '^\*\*Nguồn gốc & Bản chất của từ / cụm từ\*\*'
  'HinhAnh'     = '^\*\*Hình ảnh liên tưởng'
  'NguCanh'     = '^\*\*Ngữ cảnh sử dụng'
  'Quote'       = '^> \*'
  'DichNghia'   = 'Dịch nghĩa:'
  'NguCanhEx'   = 'Ngữ cảnh:'
}

foreach ($k in $pats.Keys) {
  $c = (Select-String -Path $File -Pattern $pats[$k]).Count
  '{0,-13} {1}' -f $k, $c
}
